from typing import cast

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.core.event_bus import EventType, Payload
from byte.core.logging import log
from byte.core.utils.list_to_multiline_text import list_to_multiline_text
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema
from byte.domain.agent.state import BaseState
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.files.service.file_service import FileService
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary


class AssistantNode(Node):
    async def boot(
        self,
        goto: str = "end_node",
        **kwargs,
    ):
        self.goto = goto

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

        # Bind tools if provided
        if context.tools is not None and len(context.tools) > 0:
            model = model.bind_tools(context.tools, parallel_tool_calls=False)

        # Assemble the chain
        runnable = context.prompt | model

        return runnable

    async def _gather_reinforcement(self, mode: str) -> list[HumanMessage]:
        """Gather reinforcement messages from various domains.

        Emits GATHER_REINFORCEMENT event and collects reinforcement
        messages that will be assembled into the prompt context.

        Args:
                mode: The AI mode being used ("main" or "weak")

        Returns:
                List containing a single HumanMessage with combined reinforcement content

        Usage: `reinforcement_messages = await self._gather_reinforcement("main")`
        """
        reinforcement_payload = Payload(
            event_type=EventType.GATHER_REINFORCEMENT,
            data={
                "reinforcement": [],
                "mode": mode,
            },
        )
        reinforcement_payload = await self.emit(reinforcement_payload)

        reinforcement_messages = reinforcement_payload.get("reinforcement", [])

        if reinforcement_messages:
            combined_content = "\n".join(f"- {msg}" for msg in reinforcement_messages)
            final_message = list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.REINFORCEMENT),
                    f"{combined_content}",
                    Boundary.close(BoundaryType.REINFORCEMENT),
                ]
            )
            return [HumanMessage(final_message)]

        return []

    async def _gather_project_hierarchy(self) -> list[HumanMessage]:
        """Gather project hierarchy for LLM understanding of project structure.

        Uses FileService to generate a concise tree-like representation
        of the project's directory structure and important files.

        Returns:
                List containing a single HumanMessage with formatted project hierarchy

        Usage: `hierarchy_messages = await self._gather_project_hierarchy()`
        """
        file_service = await self.make(FileService)
        hierarchy = await file_service.generate_project_hierarchy()

        if hierarchy:
            hierarchy_content = list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.PROJECT_HIERARCHY),
                    f"{hierarchy}",
                    Boundary.close(BoundaryType.PROJECT_HIERARCHY),
                ]
            )
            return [HumanMessage(hierarchy_content)]

        return []

    async def _gather_file_context(self, with_line_numbers=False) -> list[HumanMessage]:
        """Gather file context including read-only and editable files.

        Emits GATHER_FILE_CONTEXT event and formats the response into
        structured sections for read-only and editable files.

        Returns:
                List containing a single HumanMessage with formatted file context

        Usage: `file_messages = await self._gather_file_context()`
        """
        file_service = await self.make(FileService)

        if with_line_numbers:
            read_only_files, editable_files = await file_service.generate_context_prompt_with_line_numbers()
        else:
            read_only_files, editable_files = await file_service.generate_context_prompt()

        file_context_content = []

        if read_only_files or editable_files:
            file_context_content.extend(
                [
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
                    Boundary.open(BoundaryType.CONTEXT),
                ]
            )

        if editable_files:
            editable_content = "\n".join(editable_files)
            file_context_content.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "editable files"}),
                    f"{editable_content}",
                    Boundary.open(BoundaryType.CONTEXT),
                ]
            )

        return [HumanMessage(list_to_multiline_text(file_context_content))] if file_context_content else []

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

    async def _gather_constraints(self, state) -> list[HumanMessage]:
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
            return []

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
            return [HumanMessage(final_message)]

        return []

    async def _gather_project_context(self) -> list[HumanMessage]:
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

        project_inforamtion_and_context = []
        conventions = project_context.get("conventions", [])
        if conventions:
            conventions = "\n\n".join(conventions)
            project_inforamtion_and_context.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "coding and project conventions"}),
                    f"{conventions}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        session_docs = project_context.get("session_docs", [])
        if session_docs:
            session_docs = "\n\n".join(session_docs)
            project_inforamtion_and_context.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "session"}),
                    f"{session_docs}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        system_context = project_context.get("system_context", [])
        if system_context:
            system_info_content = "\n".join(system_context)
            project_inforamtion_and_context.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "system"}),
                    f"{system_info_content}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        return [HumanMessage(list_to_multiline_text(project_inforamtion_and_context))]

    async def __call__(self, state: BaseState, config, runtime: Runtime[AssistantContextSchema]):
        while True:
            agent_state = {**state}
            agent_state["project_inforamtion_and_context"] = await self._gather_project_context()
            agent_state["project_hierarchy"] = await self._gather_project_hierarchy()
            agent_state["file_context"] = await self._gather_file_context()
            agent_state["file_context_with_line_numbers"] = await self._gather_file_context(True)
            agent_state["reinforcement"] = await self._gather_reinforcement(runtime.context.mode)
            agent_state["constraints_context"] = await self._gather_constraints(state)

            if state.get("errors", None) is not None:
                agent_state["errors"] = await self._gather_errors(agent_state)
            else:
                agent_state["errors"] = []

            payload = Payload(
                event_type=EventType.PRE_ASSISTANT_NODE,
                data={
                    "state": agent_state,
                    "config": config,
                },
            )

            # FixtureRecorder.pickle_fixture(payload)

            payload = await self.emit(payload)
            agent_state = payload.get("state", agent_state)
            config = payload.get("config", config)

            runnable = self._create_runnable(runtime.context)

            if self._config.development.enable:
                template = runnable.get_prompts(config)
                prompt_value = await template[0].ainvoke(agent_state)
                log.info(prompt_value)

            result = await runnable.ainvoke(agent_state, config=config)

            result = cast(AIMessage, result)
            await self._track_token_usage(result, runtime.context.mode)

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
                # Re-prompt for actual response
                messages = agent_state["messages"] + [("user", "Respond with a real output.")]
                agent_state = {**agent_state, "messages": messages}
                console = await self.make(ConsoleService)
                console.print_warning_panel(
                    "AI did not provide proper output. Requesting a valid response.", title="Warning"
                )

            elif result.tool_calls and len(result.tool_calls) > 0:
                return Command(
                    goto="tools_node",
                    update={
                        "messages": [result],
                        "errors": None,
                    },
                )
            else:
                break

            await self.emit(payload)

        return Command(
            goto=self.goto,
            update={
                "messages": [result],
                "errors": None,
            },
        )
