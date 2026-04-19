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
    "3. **Round 2** (and additional rounds as needed) - Improved draft and reflection:",
    "   - Draft: Refined pseudo code based on previous reflection",
    "   - Reflection: Further improvements or confirmation it's ready",
    "4. **Tool Usage** - Execute the actual implementation using tools",
    "5. **Summary** - SHORT, CONCISE bulleted list of what was changed",
    "",
    "Requirements:",
    "- Minimum 2 rounds of drafting",
    "- Use pseudo code in drafts, NOT full implementations",
    "- Pseudocode must use structured, language-agnostic operations (e.g., ADD, REMOVE, UPDATE, CREATE, CALL, RETURN)",
    "- Do NOT use real programming syntax (no `def`, `import`, `:` etc.)",
    "- Use ```pseudo code blocks for all drafts",
    "- Reflections should be constructive and lead to improvements",
    "- Only use tools AFTER completing all drafting rounds",
    Boundary.close(BoundaryType.RESPONSE_FORMAT),
    Boundary.open(BoundaryType.EXAMPLE),
    "Example 1 - Single file edit:",
    "```",
    "# Meaning",
    "- Remove custom factorial function",
    "- Use Python's built-in math.factorial instead",
    "- Simplify code by leveraging standard library",
    "",
    "# Round 1",
    "## Draft",
    "```pseudo",
    'ADD import "math" at top',
    "",
    'REMOVE function "factorial"',
    "",
    'UPDATE function "get_factorial":',
    "    CALL math.factorial WITH n",
    "    RETURN result",
    "```",
    "",
    "## Reflection",
    "This is clear but lacks explicit file-level targeting.",
    "",
    "# Round 2",
    "## Draft",
    "```pseudo",
    "IN FILE main.py:",
    "",
    'ADD import "math" at top',
    "",
    'REMOVE function "factorial"',
    "",
    'FIND function "get_factorial":',
    "    REPLACE body WITH:",
    "        RETURN CALL math.factorial WITH n",
    "```",
    "",
    "## Reflection",
    "Now it's structured, scoped, and implementation-ready.",
    "",
    "# Begin Implementation",
    "",
    "edit_file([removed for brevity])",
    "",
    "# Changes completed:",
    "- Removed the `factorial()` function",
    "- Updated `get_factorial()` to use `math.factorial`",
    "```",
    Boundary.close(BoundaryType.EXAMPLE),
    Boundary.open(BoundaryType.EXAMPLE),
    "Example 2 - Multi-file scenario:",
    "```",
    "# Meaning",
    "- Extract hello() function into separate module",
    "- Import and use from main.py",
    "- Improve code organization",
    "",
    "# Round 1",
    "## Draft",
    "```pseudo",
    'CREATE file "hello.py"',
    "",
    "IN hello.py:",
    '    DEFINE function "hello":',
    '        PRINT "Hello"',
    "",
    "IN main.py:",
    '    REMOVE function "hello"',
    '    ADD import "hello"',
    "```",
    "",
    "## Reflection",
    "Needs clearer import usage and call structure.",
    "",
    "# Round 2",
    "## Draft",
    "```pseudo",
    'CREATE file "hello.py"',
    "",
    "IN hello.py:",
    '    DEFINE function "hello":',
    '        PRINT "Hello"',
    "",
    "IN main.py:",
    '    ADD statement: IMPORT hello FROM "hello"',
    "    ENSURE main function CALLS hello",
    "```",
    "",
    "## Reflection",
    "Structure and intent are now clear and ready.",
    "",
    "# Begin Implementation",
    "",
    "write_file(path='hello.py', [removed for brevity])",
    "edit_file(path='main.py', [removed for brevity])",
    "",
    "# Changes completed:",
    "- Created `hello.py` with `hello()` function",
    "- Updated `main.py` to import and call `hello()`",
    "```",
    Boundary.close(BoundaryType.EXAMPLE),
    Boundary.open(BoundaryType.EXAMPLE),
    "Example 3 - Modification scenario:",
    "```",
    "# Meaning",
    "- Track user login timestamps",
    "- Add last_login field to User model",
    "- Update authentication to record login time",
    "",
    "# Round 1",
    "## Draft",
    "```pseudo",
    "IN User model:",
    '    ADD field "last_login" TYPE datetime',
    "",
    "IN auth module:",
    "    ON authenticate SUCCESS:",
    "        SET user.last_login TO current time",
    "```",
    "",
    "## Reflection",
    "Needs timezone awareness and null handling.",
    "",
    "# Round 2",
    "## Draft",
    "```pseudo",
    "IN User model:",
    '    ADD field "last_login" TYPE datetime ALLOW NULL',
    "",
    "IN auth module:",
    "    IMPORT timezone-aware time utility",
    "",
    "    ON authenticate SUCCESS:",
    "        SET user.last_login TO CURRENT UTC TIME",
    "```",
    "",
    "## Reflection",
    "Timezone-safe and implementation-ready.",
    "",
    "# Begin Implementation",
    "",
    "edit_file(path='models/user.py', [removed for brevity])",
    "edit_file(path='models/auth.py', [removed for brevity])",
    "",
    "# Changes completed:",
    "- Added `last_login` field to `User` model",
    "- Updated `authenticate()` to set `last_login` timestamp",
    "```",
    Boundary.close(BoundaryType.EXAMPLE),
    "{file_context_with_line_numbers}",
    "{operating_principles}",
    Boundary.critical("All tool operations are applied immediately and are reflected in the file_context."),
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
