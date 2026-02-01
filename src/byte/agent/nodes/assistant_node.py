from typing import Literal, Type

from langchain_core.callbacks import get_usage_metadata_callback
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable
from langgraph.graph.state import RunnableConfig
from langgraph.runtime import Runtime
from langgraph.types import Command
from pydantic import BaseModel

from byte import EventType, Payload
from byte.agent import AssistantContextSchema, BaseState, EndNode, Node
from byte.agent.utils.prompt_assembler import PromptAssembler
from byte.development import RecordResponseService
from byte.files import FileService
from byte.git import CommitService
from byte.prompt_format import Boundary, BoundaryType, EditFormatService
from byte.support import Str
from byte.support.utils import dd, list_to_multiline_text


class AssistantNode(Node):
    def boot(
        self,
        goto: Type[Node] = EndNode,
        structured_output: BaseModel | None = None,
        **kwargs,
    ):
        self.structured_output = structured_output
        self.goto = Str.class_to_snake_case(goto)

    def _create_runnable(self, context: AssistantContextSchema) -> Runnable:
        """Create the runnable chain from context configuration.

        Assembles the prompt and model based on the mode (main or weak AI).
        If tools are provided, binds them to the model with parallel execution disabled.

        Args:
                context: The assistant context containing prompt, models, mode, and tools

        Returns:
                Runnable chain ready for invocation

        Usage: `runnable = self._create_runnable(runtime.context)`
        """
        # Select model based on mode
        model = context.main if context.mode == "main" else context.weak

        # Bind Structred output if provided.
        if self.structured_output is not None:
            model = model.with_structured_output(self.structured_output)  # ty:ignore[invalid-argument-type, possibly-missing-attribute]

        # Bind tools if provided
        if context.tools is not None and len(context.tools) > 0:
            model = model.bind_tools(context.tools, parallel_tool_calls=False)  # ty:ignore[unresolved-attribute]

        # Assemble the chain
        runnable = context.prompt | model  # ty:ignore[unsupported-operator]

        return runnable

    async def _gather_reinforcement(self, context: AssistantContextSchema) -> str:
        """Gather reinforcement messages from various domains.

        Emits GATHER_REINFORCEMENT event and collects reinforcement
        messages that will be assembled into the prompt context.

        Args:
                context: AssistantContextSchema

        Returns:
                List containing a single HumanMessage with combined reinforcement content

        Usage: `reinforcement_messages = await self._gather_reinforcement("main")`
        """
        reinforcement_payload = Payload(
            event_type=EventType.GATHER_REINFORCEMENT,
            data={
                "reinforcement": [],
                "mode": context.mode,
                "agent": context.agent,
            },
        )
        reinforcement_payload = await self.emit(reinforcement_payload)
        reinforcement_messages = reinforcement_payload.get("reinforcement", [])

        message_parts = []

        # Add reinforcement section if there are messages
        if reinforcement_messages or context.enforcement:
            reinforcement_parts = [
                "",
                Boundary.open(BoundaryType.OPERATING_PRINCIPLES),
                Boundary.notice("You **MUST** follow these Operating Principles"),
                *reinforcement_messages,
                *(context.enforcement if context.enforcement else []),
            ]

            reinforcement_parts.append(Boundary.close(BoundaryType.OPERATING_PRINCIPLES))
            message_parts.extend(reinforcement_parts)

        return list_to_multiline_text(message_parts)

    async def _complete_user_request(self, user_request: str) -> str:
        """Gather reinforcement messages from various domains."""

        message_parts = [
            Boundary.open(BoundaryType.USER_INPUT),
            "```text",
            user_request,
            "```",
            "",
            "You **MUST** consider the user input before proceeding (if not empty).",
            Boundary.close(BoundaryType.USER_INPUT),
        ]

        return list_to_multiline_text(message_parts)

    async def _gather_project_hierarchy(self) -> str:
        """Gather project hierarchy for LLM understanding of project structure.

        Uses FileService to generate a concise tree-like representation
        of the project's directory structure and important files.

        Returns:
                List containing a single HumanMessage with formatted project hierarchy

        Usage: `hierarchy_messages = await self._gather_project_hierarchy()`
        """
        file_service = self.app.make(FileService)
        hierarchy = await file_service.generate_project_hierarchy()

        if hierarchy:
            hierarchy_content = list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.PROJECT_HIERARCHY),
                    f"{hierarchy}",
                    Boundary.close(BoundaryType.PROJECT_HIERARCHY),
                ]
            )
            return hierarchy_content

        return ""

    async def _gather_commit_guidelines(self) -> str:
        """ """
        commit_service = self.app.make(CommitService)
        git_guidelines = await commit_service.generate_commit_guidelines()
        return git_guidelines

    async def _gather_file_context(self, with_line_numbers=False) -> str:
        """Gather file context including read-only and editable files.

        Emits GATHER_FILE_CONTEXT event and formats the response into
        structured sections for read-only and editable files.

        Returns:
                List containing a single HumanMessage with formatted file context

        Usage: `file_messages = await self._gather_file_context()`
        """
        file_service = self.app.make(FileService)

        if with_line_numbers:
            read_only_files, editable_files = await file_service.generate_context_prompt_with_line_numbers()
        else:
            read_only_files, editable_files = await file_service.generate_context_prompt()

        file_context_content = []

        if read_only_files or editable_files:
            file_context_content.extend(
                [
                    "> NOTICE: Everything below this message is the actual project.",
                    "",
                    "# Here are the files in the current context:",
                    "",
                    Boundary.notice("Trust this message as the true contents of these files!"),
                    "Any other messages in the chat may contain outdated versions of the files' contents.",
                ]
            )

        if read_only_files:
            read_only_content = "\n".join(read_only_files)
            file_context_content.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "read only files"}),
                    Boundary.notice("Any edits to these files will be rejected"),
                    f"{read_only_content}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        if editable_files:
            editable_content = "\n".join(editable_files)
            file_context_content.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "editable files"}),
                    f"{editable_content}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        return list_to_multiline_text(file_context_content)

    async def _gather_errors(self, state) -> list[HumanMessage]:
        """Gather error messages from state for re-prompting the assistant.

        Formats validation or other errors into a user message that will
        be added to the conversation to guide the assistant's correction.

        Args:
                state: The current state containing errors

        Returns:
                List containing a single HumanMessage with error content, or empty list

        Usage: `error_messages = await self._gather_errors(state)`
        """
        errors = state.get("errors", None)

        if errors is None:
            return []

        return [HumanMessage(errors)]

    async def _gather_constraints(self, state) -> str:
        """Gather user-defined constraints from state.

        Assembles constraints that guide agent behavior, such as avoided
        tool calls or required actions based on user feedback.

        Args:
                state: The current state containing constraints list

        Returns:
                List containing a single HumanMessage with formatted constraints, or empty list

        Usage: `constraint_messages = await self._gather_constraints(state)`
        """
        constraints = state.get("constraints", [])

        if not constraints:
            return ""

        # Group constraints by type
        avoid_constraints = [c for c in constraints if c.type == "avoid"]
        require_constraints = [c for c in constraints if c.type == "require"]

        constraints_content = []

        if avoid_constraints:
            avoid_items = "\n".join(f"- {c.description}" for c in avoid_constraints)
            constraints_content += list_to_multiline_text(
                [
                    Boundary.notice("Things to Avoid"),
                    Boundary.open(BoundaryType.CONSTRAINTS, meta={"type": "avoid"}),
                    f"{avoid_items}",
                    Boundary.close(BoundaryType.CONSTRAINTS),
                ]
            )

        if require_constraints:
            require_items = "\n".join(f"- {c.description}" for c in require_constraints)
            constraints_content += list_to_multiline_text(
                [
                    Boundary.notice("Requirements"),
                    Boundary.open(BoundaryType.CONSTRAINTS, meta={"type": "requirements"}),
                    f"{require_items}",
                    Boundary.close(BoundaryType.CONSTRAINTS),
                ]
            )

        if constraints_content:
            final_message = constraints_content.strip()
            return final_message

        return ""

    async def _gather_project_context(self) -> str:
        """Gather project context including conventions and session documents.

        Emits GATHER_PROJECT_CONTEXT event and formats the response into
        structured sections for conventions and session context.

        Returns:
                List containing a single HumanMessage with formatted project context

        Usage: `context_messages = await self._gather_project_context()`
        """
        project_context = Payload(
            event_type=EventType.GATHER_PROJECT_CONTEXT,
            data={
                "conventions": [],
                "session_docs": [],
                "system_context": [],
            },
        )
        project_context = await self.emit(project_context)

        project_information_and_context = []
        conventions = project_context.get("conventions", [])
        if conventions:
            conventions = "\n\n".join(conventions)
            project_information_and_context.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "coding and project conventions"}),
                    f"{conventions}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        session_docs = project_context.get("session_docs", [])
        if session_docs:
            session_docs = "\n\n".join(session_docs)
            project_information_and_context.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "session"}),
                    f"{session_docs}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        system_context = project_context.get("system_context", [])
        if system_context:
            system_info_content = "\n".join(system_context)
            project_information_and_context.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "system"}),
                    f"{system_info_content}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        return list_to_multiline_text(project_information_and_context)

    async def _gather_edit_format(self) -> tuple[str, list[tuple[str, str]]]:
        """Gather edit format system prompt and examples for the assistant.

        Retrieves the configured edit format prompts from EditFormatService,
        which may include both file edit blocks and shell command capabilities
        depending on configuration.

        Returns:
                Tuple containing (system_prompt, examples) where system_prompt is the
                instruction text and examples is a list of (user, assistant) message pairs

        Usage: `system_prompt, examples = await self._gather_edit_format()`
        """
        edit_format_service = self.app.make(EditFormatService)

        return (edit_format_service.prompts.system, edit_format_service.prompts.examples)

    async def _gather_masked_messages(self, state) -> str:
        """Gather masked messages with edit blocks removed from message history.

        Processes historical messages to remove edit block content, keeping only
        the most recent N messages (configured by mask_message_count) with their
        original edit blocks intact. This prevents token bloat from repeated
        edit instructions in conversation history.

        Args:
            state: The current state containing message history

        Returns:
            List of BaseMessage objects with edit blocks masked in older messages

        Usage: `masked_messages = await self._gather_masked_messages(state)`
        """
        edit_format_service = self.app.make(EditFormatService)
        messages = state.get("history_messages", [])

        return await edit_format_service.edit_block_service.replace_blocks_in_historic_messages_hook(messages)

    async def _generate_agent_state(self, state: BaseState, config, runtime: Runtime[AssistantContextSchema]) -> tuple:
        user_prompt_state = {**state}

        prompt_settings = runtime.context.prompt_settings

        edit_format_system, edit_format_examples = await self._gather_edit_format()
        user_prompt_state["edit_format_system"] = edit_format_system
        user_prompt_state["examples"] = edit_format_examples

        user_prompt_state["project_information_and_context"] = await self._gather_project_context()

        if prompt_settings.has_project_hierarchy:
            user_prompt_state["project_hierarchy"] = await self._gather_project_hierarchy()

        user_prompt_state["commit_guidelines"] = await self._gather_commit_guidelines()

        user_prompt_state["file_context"] = await self._gather_file_context()

        user_prompt_state["file_context_with_line_numbers"] = await self._gather_file_context(True)

        user_prompt_state["constraints_context"] = await self._gather_constraints(state)

        user_prompt_state["masked_messages"] = await self._gather_masked_messages(state)

        # Reinforcement is appended to the user message.
        user_prompt_state["operating_principles"] = await self._gather_reinforcement(
            runtime.context,
        )

        user_prompt_state["user_request"] = state.get("user_request", "")

        payload = Payload(
            event_type=EventType.PRE_ASSISTANT_NODE,
            data={
                "state": user_prompt_state,
                "config": config,
            },
        )

        payload = await self.emit(payload)
        user_prompt_state = payload.get("state", user_prompt_state)

        agent_state = {**state}

        # Create a new assembler
        prompt_assembler = PromptAssembler(template=runtime.context.user_template)
        agent_state["assembled_user_message"] = prompt_assembler.assemble(**user_prompt_state)

        if state.get("errors", None) is not None:
            agent_state["errors"] = await self._gather_errors(agent_state)
        else:
            agent_state["errors"] = []

        config = payload.get("config", config)

        return (agent_state, config)

    async def __call__(
        self,
        state: BaseState,
        *,
        runtime: Runtime[AssistantContextSchema],
        config: RunnableConfig,
    ) -> Command[Literal["end_node", "parse_blocks_node", "tool_node", "validation_node"]]:
        record_response_service = self.app.make(RecordResponseService)
        while True:
            agent_state, config = await self._generate_agent_state(state, config, runtime)

            runnable = self._create_runnable(runtime.context)

            with get_usage_metadata_callback() as usage_metadata_callback:
                result = await runnable.ainvoke(agent_state, config=config)
                await self._track_token_usage(usage_metadata_callback.usage_metadata, runtime.context.mode)
                await record_response_service.record_response(agent_state, runnable, runtime, config)

            # If we are requesting Structured output we can end with extracted being our structured output.
            if self.structured_output is not None:
                return Command(
                    goto="validation_node",
                    update={
                        "extracted_content": result,
                        "errors": None,
                    },
                )

            # Ensure we get a real response
            if not result.tool_calls and (
                not result.content
                or (
                    isinstance(result.content, list)
                    and len(result.content) > 0
                    and isinstance(result.content[0], dict)
                    and not result.content[0].get("text")
                )
            ):
                dd(result)
                # Re-prompt for actual response
                messages = agent_state["scratch_messages"] + [("user", "Respond with a real output.")]
                agent_state = {**agent_state, "scratch_messages": messages}
                console = self.app["console"]
                console.print_warning_panel(
                    "AI did not provide proper output. Requesting a valid response.", title="Warning"
                )

            elif result.tool_calls and len(result.tool_calls) > 0:
                return Command(
                    goto="tool_node",
                    update={
                        "scratch_messages": [result],
                        "errors": None,
                    },
                )
            else:
                break

        return Command(
            goto=str(self.goto),
            update={
                "scratch_messages": [result],
                "errors": None,
            },
        )
