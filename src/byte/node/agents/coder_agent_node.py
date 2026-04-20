from typing import Literal, Type

from langchain.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.files import delete_file, edit_file, replace_file, write_file
from byte.llm import LLMService, ModelSchema
from byte.node import (
    BaseAgentNode,
    BaseNode,
)
from byte.node.nodes import EndNode
from byte.orchestration import AssistantContextSchema, BaseState, preamble
from byte.support import Boundary, BoundaryType, Str
from byte.support.utils import extract_content_from_message, list_to_multiline_text
from byte.tui import Messages, Status

coder_user_template = [
    Boundary.open(BoundaryType.PLAN),
    "```text",
    "{user_request}",
    "```",
    "",
    "You **MUST** follow the plan provided above.",
    Boundary.close(BoundaryType.PLAN),
    Boundary.open(BoundaryType.OPERATING_CONSTRAINTS),
    "- Follow the agent plan exactly as specified — implement each step in order",
    "- Do not deviate from or add to the plan unless necessary to fix an error",
    "- Always use best practices when coding",
    "- Respect and use existing conventions, libraries, etc that are already present in the code base",
    "- Take requests for changes to the supplied code",
    "- Keep changes simple don't build more then what is asked for",
    Boundary.close(BoundaryType.OPERATING_CONSTRAINTS),
    Boundary.open(BoundaryType.RESPONSE_FORMAT),
    "Your response must follow this structured format:",
    "",
    "1. **Meaning** - A bulleted summary of key points from the plan",
    "2. **Round 1** - First draft and reflection:",
    "   - Draft: Pseudo code implementation of the requested change",
    "   - Reflection: Analysis of how it can be improved",
    "3. **Round 2** - Improved draft and reflection:",
    "   - Draft: Refined pseudo code based on previous reflection",
    "   - Reflection: Further improvements",
    "4. **Round 3** - Final draft and validation:",
    "   - Draft: Final pseudo code ready for execution",
    "   - Reflection: Confirm no further improvements needed",
    "5. **Tool Usage (MANDATORY)** - Execute the implementation using tool calls",
    "6. **Summary** - SHORT, CONCISE bulleted list of what was changed",
    "",
    "Requirements:",
    "- Minimum 3 rounds of drafting",
    "- Use pseudo code in drafts, NOT full implementations",
    "- Pseudocode must use structured, language-agnostic operations (e.g., ADD, REMOVE, UPDATE, CREATE, CALL, RETURN)",
    "- Do NOT use real programming syntax (no `def`, `import`, `:` etc.)",
    "- Use ```pseudo code blocks for all drafts",
    "- Reflections should be constructive and lead to improvements",
    "- Tool Usage section MUST contain real tool calls (not descriptions)",
    "- Only use tools AFTER completing all drafting rounds",
    Boundary.close(BoundaryType.RESPONSE_FORMAT),
    Boundary.open(BoundaryType.EXAMPLE),
    "Example 1 - Single file edit:",
    "```",
    "# Meaning",
    "- Remove custom factorial function",
    "- Use math.factorial instead",
    "",
    "# Round 1",
    "## Draft",
    "```pseudo",
    'ADD import "math" at top',
    'REMOVE function "factorial"',
    "UPDATE function get_factorial TO use math.factorial",
    "```",
    "",
    "## Reflection",
    "Needs file-level specificity.",
    "",
    "# Round 2",
    "## Draft",
    "```pseudo",
    "IN FILE main.py:",
    '    ADD import "math"',
    '    REMOVE function "factorial"',
    '    FIND function "get_factorial"',
    "        REPLACE body WITH math.factorial call",
    "```",
    "",
    "## Reflection",
    "Structure is clear but replacement not explicit enough.",
    "",
    "# Round 3",
    "## Draft",
    "```pseudo",
    "IN FILE main.py:",
    '    ADD import "math" at top',
    '    DELETE entire function "factorial"',
    '    LOCATE function "get_factorial"',
    "        REPLACE return logic WITH:",
    "            RETURN CALL math.factorial WITH n",
    "```",
    "",
    "## Reflection",
    "Fully explicit and ready for execution.",
    "",
    "[Tool Usage (MANDATORY) - Make tool calls to make the change.]",
    # "edit_file(path='main.py', old_string='...', new_string='...')",
    "",
    "# Summary",
    "- Removed factorial function",
    "- Updated get_factorial",
    "```",
    Boundary.close(BoundaryType.EXAMPLE),
    Boundary.open(BoundaryType.EXAMPLE),
    "Example 2 - Multi-file:",
    "```",
    "# Meaning",
    "- Extract hello() into new module",
    "",
    "# Round 1",
    "## Draft",
    "```pseudo",
    'CREATE file "hello.py"',
    "MOVE hello function",
    "```",
    "",
    "## Reflection",
    "Too vague.",
    "",
    "# Round 2",
    "## Draft",
    "```pseudo",
    'CREATE file "hello.py"',
    "IN hello.py DEFINE hello",
    "REMOVE hello from main.py",
    "```",
    "",
    "## Reflection",
    "Missing import wiring.",
    "",
    "# Round 3",
    "## Draft",
    "```pseudo",
    'CREATE file "hello.py"',
    "IN hello.py:",
    '    DEFINE function "hello"',
    '        PRINT "Hello"',
    "IN main.py:",
    '    REMOVE function "hello"',
    "    ADD import hello FROM hello.py",
    "    CALL hello in main flow",
    "```",
    "",
    "## Reflection",
    "Ready.",
    "",
    "[Tool Usage (MANDATORY) - Make tool calls to make the change.]",
    # "write_file(path='hello.py', content='...')",
    # "edit_file(path='main.py', old_string='...', new_string='...')",
    # "",
    "# Summary",
    "- Created hello.py",
    "- Updated main.py",
    "```",
    Boundary.close(BoundaryType.EXAMPLE),
    Boundary.open(BoundaryType.EXAMPLE),
    "Example 3 - Modification:",
    "```",
    "# Meaning",
    "- Add last_login tracking",
    "",
    "# Round 1",
    "## Draft",
    "```pseudo",
    "ADD last_login field",
    "SET timestamp on login",
    "```",
    "",
    "## Reflection",
    "Too generic.",
    "",
    "# Round 2",
    "## Draft",
    "```pseudo",
    "IN User:",
    "    ADD datetime field",
    "IN auth:",
    "    SET login time",
    "```",
    "",
    "## Reflection",
    "Needs timezone handling.",
    "",
    "# Round 3",
    "## Draft",
    "```pseudo",
    "IN models/user.py:",
    '    ADD field "last_login" TYPE datetime ALLOW NULL',
    "IN auth flow:",
    "    ON successful login:",
    "        SET last_login TO CURRENT UTC TIME",
    "```",
    "",
    "## Reflection",
    "Complete and correct.",
    "",
    "[Tool Usage (MANDATORY) - Make tool calls to make the change.]",
    # "edit_file(path='models/user.py', old_string='...', new_string='...')",
    # "edit_file(path='models/auth.py', old_string='...', new_string='...')",
    # "",
    "# Summary",
    "- Added last_login",
    "- Updated auth logic",
    "```",
    Boundary.close(BoundaryType.EXAMPLE),
    "{file_context_with_line_numbers}",
    "{operating_principles}",
    Boundary.critical("All tool operations are applied immediately and are reflected in the file_context."),
    Boundary.critical("REMEMBER: You MUST use the tools AFTER completing all drafting rounds."),
]

coder_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.ROLE),
                    preamble(),
                    "Act as an expert software developer.",
                    Boundary.close(BoundaryType.ROLE),
                ]
            ),
        ),
        # ("placeholder", "{examples}"),
        ("user", "{assembled_user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)


class CoderAgentNode(BaseAgentNode):
    def boot(
        self,
        goto: Type[BaseNode] = EndNode,
        **kwargs,
    ):
        """
        Initialize the CoderAgentNode with a target node to route to after execution.

        Args:
            goto: The target node class to route to after the agent completes. Defaults to EndNode.
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        self.goto = Str.class_to_snake_case(goto)

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_prompt(self):
        return coder_prompt

    def get_user_template(self):
        return coder_user_template

    def get_tools(self):
        return [edit_file, write_file, delete_file, replace_file]

    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        agent_state, config = await self.generate_agent_state(state, config)
        runnable = self.create_runnable()
        record_response_service = self.app.make(RecordResponseService)

        await self.emit_tui(Messages.AddHeading("Coder Agent", "text-primary"))
        await self.emit_tui(Messages.Response(status=Status.PENDING, with_indicator=True))

        await record_response_service.record_response(agent_state, runnable, "coder_agent", config)
        result = await runnable.ainvoke(agent_state, config=config)

        await self.emit_tui(Messages.Response(status=Status.SUCCESS))

        if result.tool_calls and len(result.tool_calls) > 0:
            return self.route_to(
                "tool_node",
                {
                    "scratch_messages": [result],
                    "errors": None,
                },
            )

        msg = extract_content_from_message(result)

        return self.route_to(self.goto, {"scratch_messages": AIMessage(msg)})
