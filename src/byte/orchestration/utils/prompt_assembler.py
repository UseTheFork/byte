import re
from typing import TYPE_CHECKING, TypeVar

from typing_extensions import List

from byte.conventions import ConventionContextService
from byte.files import FileService
from byte.git import CommitService
from byte.llm import ModelSchema
from byte.orchestration import BaseState, OrchestrationEvents
from byte.support import Boundary, BoundaryType, Str
from byte.support.mixins import Bootable, Eventable
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    pass

T = TypeVar("T")


class PromptAssembler(Bootable, Eventable):
    """Assembles prompts from templates by gathering context from various services.

    Coordinates collection of file context, project hierarchy, constraints,
    reinforcement messages, and other prompt components, then assembles them
    into a complete prompt using template replacement.

    Usage: `assembler = PromptAssembler(template=["Hello {name}"])`
    Usage: `state = await assembler.generate_state(state, config, context)`
    Usage: `prompt = assembler.assemble(name="World", age=30)`
    """

    def boot(self, template: List[str] | None, **kwargs):
        if template is None or len(template) == 0:
            raise ValueError("template parameter is required and cannot be empty")

        self.template = template

    async def _gather_reinforcement(self, agent: str, model_schema: ModelSchema) -> str:
        """Gather reinforcement messages from various domains.

        Emits GATHER_REINFORCEMENT event and collects reinforcement
        messages that will be assembled into the prompt context.

        Args:
                context: AssistantContextSchema

        Returns:
                List containing a single HumanMessage with combined reinforcement content

        Usage: `reinforcement_messages = await self._gather_reinforcement("main")`
        """
        reinforcement_payload = await self.emit(
            OrchestrationEvents.GatherReinforcement(
                model=model_schema.model,
                provider=model_schema.provider,
                agent=agent,
                reinforcement=[],
            )
        )
        reinforcement_messages = reinforcement_payload.reinforcement

        message_parts = []

        # Add reinforcement section if there are messages
        # if reinforcement_messages or context.enforcement:
        # TODO: This needs to be fixed `reinforcements` should just come from the agent now.
        if reinforcement_messages:
            reinforcement_parts = [
                "",
                Boundary.open(BoundaryType.OPERATING_PRINCIPLES),
                Boundary.notice("You **MUST** follow these Operating Principles"),
                *reinforcement_messages,
                *([]),
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
                    "# Here are the files in the current context:",
                    "",
                    Boundary.notice("Trust the bellow as the true contents of these files!"),
                    "Any other messages may contain outdated versions of the files' contents.",
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
            final_message = constraints_content.strip()  # ty:ignore[unresolved-attribute]
            return final_message

        return ""

    async def gather_available_conventions(self, state: BaseState) -> str:
        """ """
        convention_context_service = self.app.make(ConventionContextService)
        return await convention_context_service.get_available_conventions(state)

    async def _gather_project_context(self) -> str:
        """Gather project context including conventions and session documents.

        Emits GATHER_PROJECT_CONTEXT event and formats the response into
        structured sections for conventions and session context.

        Returns:
                List containing a single HumanMessage with formatted project context

        Usage: `context_messages = await self._gather_project_context()`
        """

        project_context = await self.emit(OrchestrationEvents.GatherProjectContext())

        project_information_and_context = []
        conventions = project_context.conventions
        if conventions:
            conventions = "\n\n".join(conventions)
            project_information_and_context.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "coding and project conventions"}),
                    f"{conventions}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        session_docs = project_context.session_docs
        if session_docs:
            session_docs = "\n\n".join(session_docs)
            project_information_and_context.extend(
                [
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "session"}),
                    f"{session_docs}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        system_context = project_context.system_context
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

    async def generate_state(self, state: BaseState, agent, model_schema: ModelSchema) -> dict:
        user_prompt_state = {**state}

        agent = Str.class_to_snake_case(agent)

        if state.get("metadata", {}).prompt_settings.has_project_information_and_context:
            user_prompt_state["project_information_and_context"] = await self._gather_project_context()

        if state.get("metadata", {}).prompt_settings.has_project_hierarchy:
            user_prompt_state["project_hierarchy"] = await self._gather_project_hierarchy()

        user_prompt_state["commit_guidelines"] = await self._gather_commit_guidelines()

        if state.get("metadata", {}).prompt_settings.has_file_context:
            user_prompt_state["file_context"] = await self._gather_file_context()

        if state.get("metadata", {}).prompt_settings.has_file_context:
            user_prompt_state["file_context_with_line_numbers"] = await self._gather_file_context(True)

        user_prompt_state["constraints_context"] = await self._gather_constraints(state)

        messages = state.get("history_messages", [])
        user_prompt_state["masked_messages"] = messages

        user_prompt_state["available_conventions"] = await self.gather_available_conventions(state)

        # Reinforcement is appended to the user message.
        user_prompt_state["operating_principles"] = await self._gather_reinforcement(agent, model_schema)

        user_prompt_state["user_request"] = state.get("user_request", "")

        return user_prompt_state

    def assemble(self, **replacements) -> str:
        """Replace {placeholder} tokens in template with provided values.

        Automatically removes lines containing only placeholders that don't have corresponding values.
        Placeholders are expected to be on their own line with nothing else.

        Usage: `assembler.assemble(name="World", age=30)`
        """

        result_lines = []
        placeholder_pattern = r"^\{([^}]+)\}$"

        for line in self.template:
            match = re.match(placeholder_pattern, line)
            if match:
                # Line contains only a placeholder
                key = match.group(1)
                if key in replacements:
                    # Replace with the value
                    value = replacements[key]
                    result_lines.append(value if isinstance(value, str) else str(value))
                # If key not in replacements, skip this line (remove it)
            else:
                # Not a placeholder line, keep as-is
                result_lines.append(line)

        return list_to_multiline_text(result_lines)
