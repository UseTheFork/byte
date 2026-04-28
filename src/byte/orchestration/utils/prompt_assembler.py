import asyncio
import re
from typing import TYPE_CHECKING, TypeVar

from langchain.messages import AIMessage, HumanMessage
from langchain_core.messages import BaseMessage

from byte.conventions import ConventionContextService
from byte.files import FileService
from byte.git import CommitService
from byte.orchestration import BaseState, OrchestrationEvents
from byte.skills import LoadSkillTool, SkillLoaderService, SkillTrackerService
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.support.mixins import Bootable, Eventable
from byte.support.utils import list_to_multiline_text
from byte.tools import ToolMessage

if TYPE_CHECKING:
    from byte.node import BaseAgentNode

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

    def boot(self, agent_node: BaseAgentNode | None, **kwargs):

        if agent_node is None:
            raise ValueError("agent_node is required and cannot be empty")

        self.agent_node = agent_node
        template = agent_node.get_user_template()
        if template is None or len(template) == 0:
            raise ValueError("user template is required and cannot be empty")

        self.template = template

        model_schema, _ = self.agent_node.get_model()
        self.model_schema = model_schema

        self.prompt_state = {}

    async def _gather_reinforcement(self) -> str:
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
                model=self.model_schema.model,
                provider=self.model_schema.provider,
                agent=self.agent_node.name,
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
                Section.start(SectionType.OPERATING_PRINCIPLES),
                Section.important("You **MUST** follow these Operating Principles"),
                *reinforcement_messages,
                *([]),
                Section.end(),
            ]

            message_parts.extend(reinforcement_parts)

        return list_to_multiline_text(message_parts)

    async def _complete_user_request(self, user_request: str) -> str:
        """Gather reinforcement messages from various domains."""

        message_parts = [
            Section.start(SectionType.USER_INPUT),
            "```",
            user_request,
            "```",
            "",
            "You **MUST** consider the user input before proceeding (if not empty).",
            Section.end(),
        ]

        return list_to_multiline_text(message_parts)

    async def _generate_available_skills(self) -> str:
        """ """
        skill_tracker_service = self.app.make(SkillTrackerService)
        skill_loader_service = self.app.make(SkillLoaderService)

        # Get only the skills that haven't been loaded yet
        unloaded_names = skill_tracker_service.get_unloaded_names()
        unloaded_skills = {name: skill for name, skill in skill_loader_service.skills.items() if name in unloaded_names}

        skills_xml = skill_loader_service.skills_to_prompt_xml(unloaded_skills)

        if not skills_xml:
            return ""

        message_parts = [
            Section.start(SectionType.AVALIABLE_SKILLS),
            "```",
            skills_xml,
            "```",
            Section.sub_heading("Skills Usage", 2),
            f"The `{Boundary.open(BoundaryType.DESCRIPTION)}` of each skill is a TRIGGER — it tells you *when* a skill applies. It is NOT a specification of what the skill does or how to do it. The procedure, scripts, commands, references, and required flags live only in the SKILL.md body. You do not know what a skill actually does until you have read its SKILL.md.",
            "",
            "MANDATORY activation flow:",
            f"1. Scan `{Boundary.open(BoundaryType.AVAILABLE_SKILLS)}` against the current user task.",
            f"2. If any skill's `{Boundary.open(BoundaryType.DESCRIPTION)}` matches, call the `{LoadSkillTool.name}` with its `{Boundary.open(BoundaryType.NAME)}` EXACTLY as shown — before any other tool call that performs the task.",
            "3. Read the entire SKILL.md and follow its instructions.",
            "4. Only then execute the task, using the skill's prescribed commands/tools.",
            "",
            "Do NOT skip step 2 because you think you already know how to do the task. Do NOT infer a skill's behavior from its name or description. If you find yourself about to run `edit`, or any task-doing tool for a skill-eligible request without having just viewed the SKILL.md, stop and load the skill first.",
            Section.end(),
        ]

        return list_to_multiline_text(message_parts)

    async def _generate_loaded_skills(self) -> str:
        """Generate prompt content containing the instructions of loaded skills."""
        skill_tracker_service = self.app.make(SkillTrackerService)
        skill_loader_service = self.app.make(SkillLoaderService)

        loaded_names = skill_tracker_service.loaded_names()
        if not loaded_names:
            return ""

        message_parts = [
            Section.start(SectionType.SKILLS),
        ]

        for name in loaded_names:
            skill = skill_loader_service.get_skill(name)
            if skill is None:
                continue
            message_parts.extend(
                [
                    Boundary.open(BoundaryType.SKILL, meta={"name": name}),
                    skill.instructions,
                    Boundary.close(BoundaryType.SKILL),
                    "",
                ]
            )

        if not message_parts:
            return ""

        message_parts.extend(Section.end())

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

    async def _gather_modified_messages(self, state) -> str:
        """ """
        messages: list[BaseMessage] = state.get("history_messages", [])
        messages = self.agent_node.filter_message_history(messages)

        # Create masked_messages list identical to messages except for processed AIMessages

        masked_messages = [
            Section.start(SectionType.CONVERSATION_HISTORY),
            "",
            "Below is the conversation history between Byte agents and the user.",
            "",
            f"Messages are wrapped in XML tags corresponding to their type (e.g. `{Boundary.open(BoundaryType.AGENT_MESSAGE)}`, `{Boundary.open(BoundaryType.USER_MESSAGE)}`, `{Boundary.open(BoundaryType.TOOL_CALL)}`).",
            "",
            "```",
        ]

        if not messages:
            masked_messages.extend(
                [
                    "The conversation history is empty.",
                    "```",
                ]
            )
            return list_to_multiline_text(masked_messages)

        for message in messages:
            masked_messages.append(message.text)

        masked_messages.extend(
            [
                "```",
                "",
                Section.important("You **MUST** consider the conversation history before proceeding."),
                Section.end(),
            ]
        )

        return list_to_multiline_text(masked_messages)

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
                    Section.sub_heading("Project Files", 2),
                    "Here are the files in the current context",
                    "",
                ]
            )

        if read_only_files:
            read_only_content = "\n".join(read_only_files)
            file_context_content.extend(
                [
                    Section.sub_heading("Read Only Files", 3),
                    "Any edits to these files will be rejected",
                    "",
                    "```",
                    f"{read_only_content}",
                    "```",
                ]
            )

        if editable_files:
            editable_content = "\n".join(editable_files)
            file_context_content.extend(
                [
                    Section.sub_heading("Editable Files", 3),
                    "",
                    "```",
                    f"{editable_content}",
                    "```",
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
                    "# ",
                    Boundary.open(BoundaryType.CONTEXT, meta={"type": "system"}),
                    f"{system_info_content}",
                    Boundary.close(BoundaryType.CONTEXT),
                ]
            )

        return list_to_multiline_text(project_information_and_context)

    def generate_pending_agent_state(self, state: BaseState) -> list[BaseMessage]:

        masked_messages = []
        messages = state["scratch_messages"]

        if not messages:
            masked_messages.append("Please provide any additional context I may need for this task.")

        for message in messages:
            if isinstance(message, AIMessage):
                masked_messages.extend(
                    [
                        "",
                        Boundary.open(BoundaryType.AGENT_MESSAGE),
                        f"{message.text}",
                        Boundary.close(BoundaryType.AGENT_MESSAGE),
                        "",
                    ]
                )
            elif isinstance(message, ToolMessage):
                masked_messages.extend(
                    [
                        "",
                        Boundary.open(BoundaryType.TOOL_CALL, meta={"tool": str(message.name)}),
                        f"{message.text}",
                        Boundary.close(BoundaryType.TOOL_CALL),
                        "",
                    ]
                )

        return [AIMessage(content=list_to_multiline_text(masked_messages))]

    async def generate_state(self, state: BaseState, extra: dict | None = {}) -> dict:
        user_prompt_state = {**state, **(extra or {})}

        # Create dictionary to map task names to their coroutines
        tasks = {}

        # Add conditional tasks
        if state.get("metadata", {}).prompt_settings.has_project_information_and_context:
            tasks["project_context"] = self._gather_project_context()
        if state.get("metadata", {}).prompt_settings.has_project_hierarchy:
            tasks["project_hierarchy"] = self._gather_project_hierarchy()

        # Always executed tasks
        tasks.update(
            {
                "modified_messages": self._gather_modified_messages(state),
                "commit_guidelines": self._gather_commit_guidelines(),
                "constraints": self._gather_constraints(state),
                "available_conventions": self.gather_available_conventions(state),
                "available_skills": self._generate_available_skills(),
                "loaded_skills": self._generate_loaded_skills(),
                "reinforcement": self._gather_reinforcement(),
                "user_request": self._complete_user_request(state.get("user_request", "")),
            }
        )

        # Handle file context tasks
        if state.get("metadata", {}).prompt_settings.has_file_context:
            tasks.update(
                {
                    "file_context": self._gather_file_context(),
                    "file_context_with_line_numbers": self._gather_file_context(True),
                }
            )

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks.values())

        # Map results back to their keys
        results_dict = dict(zip(tasks.keys(), results))

        # Build the state dictionary
        if "project_context" in results_dict:
            user_prompt_state["project_information_and_context"] = results_dict["project_context"]
        if "project_hierarchy" in results_dict:
            user_prompt_state["project_hierarchy"] = results_dict["project_hierarchy"]

        user_prompt_state.update(
            {
                "modified_messages": results_dict["modified_messages"],
                "commit_guidelines": results_dict["commit_guidelines"],
                "constraints_context": results_dict["constraints"],
                "available_skills": results_dict["available_skills"],
                "loaded_skills": results_dict["loaded_skills"],
                "available_conventions": results_dict["available_conventions"],
                "operating_principles": results_dict["reinforcement"],
                "user_request": results_dict["user_request"],
            }
        )

        if "file_context" in results_dict:
            user_prompt_state.update(
                {
                    "file_context": results_dict["file_context"],
                    "file_context_with_line_numbers": results_dict["file_context_with_line_numbers"],
                }
            )

        self.prompt_state = user_prompt_state

        return user_prompt_state

    def assemble_user_message(self, **replacements) -> str:
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

    def generate_refreshed_context_state(self, state: BaseState) -> list[BaseMessage]:
        """ """
        refreshed_context_message = list_to_multiline_text(
            [
                self.prompt_state["loaded_skills"],
                Section.start(SectionType.PROJECT_STATE),
                "#id-dhd88-asx-4857",
                "",
                "Below is the current state of the project. It includes all your changes as a result of previous tool calls that have been masked for brevity.",
                "",
                Section.important("You MUST trust this information as the current state of the files etc."),
                "",
                self.prompt_state["file_context_with_line_numbers"],
                "",
                Section.end(),
                "",
                self.epilogue(),
            ]
        )

        return [HumanMessage(content=refreshed_context_message)]

    def epilogue(self) -> str:
        history_messages = self.prompt_state.get("history_messages", [])

        lines = [
            Section.start(SectionType.RESUME_FORMAT),
            "",
        ]

        if not history_messages:
            lines.append("> **Remember**: This is your first response so you are starting at the FIRST step.")
        else:
            lines.extend(
                [
                    f"> **Remember**: This is a followup response. Make sure to consider the {Section.ref(SectionType.RESPONSE_FORMAT)} section and plan accordingly."
                ]
            )

        return list_to_multiline_text(lines)
