import asyncio
import re
from datetime import datetime
from typing import TYPE_CHECKING, TypeVar

from langchain_core.messages import BaseMessage

from byte.files import FileService
from byte.git import CommitService
from byte.orchestration import BaseState, OrchestrationEvents
from byte.skills import LoadSkillTool, SkillLoaderService, SkillTrackerService
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.support.mixins import Bootable, Eventable
from byte.support.utils import list_to_multiline_text

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
        user_template = agent_node.get_user_template()
        if user_template is None or len(user_template) == 0:
            raise ValueError("user template is required and cannot be empty")

        self.user_template = user_template

        system_template = agent_node.get_system_template()
        if system_template is None or len(system_template) == 0:
            raise ValueError("system template is required and cannot be empty")

        self.system_template = system_template

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

    async def _generate_project_environment(self) -> str:
        """ """
        root_path = self.app.root_path()

        # TODO: https://github.com/charmbracelet/crush/blob/64c47cbbb3f0825432876786fb72737089732f55/internal/agent/templates/coder.md.tpl
        message_parts = [
            Section.start(SectionType.PROJECT_ENVIRONMENT),
            f"Working directory: {root_path}",
            f"Today's date: {datetime.now().strftime('%Y-%m-%d')}",
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
            return list_to_multiline_text(
                [
                    Section.start(SectionType.AVALIABLE_SKILLS),
                    "```",
                    "NO skills avaliable.",
                    "```",
                ]
            )

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

    async def _gather_file_context(self) -> str:
        """Gather file context including read-only and editable files.

        Emits GATHER_FILE_CONTEXT event and formats the response into
        structured sections for read-only and editable files.

        Returns:
                List containing a single HumanMessage with formatted file context

        Usage: `file_messages = await self._gather_file_context()`
        """
        file_service = self.app.make(FileService)

        read_only_files, editable_files = await file_service.generate_context_prompt_with_line_numbers()

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

    async def _gather_project_context(self) -> str:
        """Gather project context including conventions and session documents.

        Emits GATHER_PROJECT_CONTEXT event and formats the response into
        structured sections for conventions and session context.

        Returns:
                List containing a single HumanMessage with formatted project context

        Usage: `context_messages = await self._gather_project_context()`
        """

        project_context = await self.emit(OrchestrationEvents.GatherProjectContext())

        project_information_and_context = [
            Section.start(SectionType.REFERENCE_MATERIALS),
            "",
        ]
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

        project_information_and_context.append(Section.end())

        return list_to_multiline_text(project_information_and_context)

    async def _generate_preamble(self) -> str:
        lines = [
            Section.start(SectionType.INTRODUCTION),
            "You are Byte, a CLI agent specializing in software engineering tasks. Your primary goal is to help users safely and effectively.",
            "",
            "Conversations are always structured in a consistent format:",
            "- **System Prompt** — Sets your role, identity, and core behavioral guidelines.",
            "- **User Message** — Contains the conversation history, the current user request, task instructions, response format, and other relevant context. Sections are clearly labelled with `# Section: FOO [section-foo]` headings.",
            "- **Agent Message** — A summarized representation of your previous responses and tool calls, modified for brevity.",
            f"- **User Message ({SectionType.PROJECT_STATE})** — An automatically generated message containing the most up-to-date state of all relevant files and system context. This message is regenerated after **every** tool call to reflect the latest changes.",
            "",
            "The instructions provided by the user are ALWAYS split up into sections. Sections always start with `# Section: `.",
            f"- `{SectionType.USER_INPUT}` - Contains the users request. Pay close attention to this section.",
            f"- `{SectionType.ROLE}` - Contains information about your specific role as part of the users request.",
            f"- `{SectionType.RESPONSE_FORMAT}` - How you should structure your response format.",
            f"- `{SectionType.TASK}` - This section includes the task the user would like you to complete.",
            "",
            "To make parsing the user content simpler sections use XML tags. XML tags may include additional attributes that relate directly with the content they are surrounding. For example:",
            f"`{Boundary.open(BoundaryType.FILE, meta={'source': 'foo/bar.py', 'language': 'py', 'mode': 'read-only'})}`",
            "The example is a file tag with attributes representing the mode of the file (if you can edit the file), the source (the path), and its language.",
            "",
            "Here is a guide for XML tags you will encounter.",
            f"- `{Boundary.open(BoundaryType.FILE)}` - The file tag wraps file content provided for context. Attributes include `source` (the file path), `language` (the programming language), and `mode` (either `read-only` or `editable`, indicating whether you can modify the file).",
            f"- `{Boundary.open(BoundaryType.SESSION_CONTEXT)}` - The session_context tag wraps supplementary context documents added by the user for the current session. Attributes include `type` (the source type, e.g. `file`, `web`, or `agent`) and `key` (a unique identifier for the context item).",
            f"- `{Boundary.open(BoundaryType.EXAMPLE)}` - The example tag wraps example content blocks used to demonstrate expected input, output, or behaviour. Use the enclosed content as a reference for formatting or structure.",
            f"- `{Boundary.open(BoundaryType.AGENT_MESSAGE)}` - The agent_message tag wraps a response produced by an agent. Attributes include `agent_type` (the name of the agent that produced the message).",
            f"- `{Boundary.open(BoundaryType.TOOL_CALL)}` - The tool_call tag wraps a summary of a tool invocation performed by an agent, including the tool name and its execution status.",
            f"- `{Boundary.open(BoundaryType.USER_MESSAGE)}` - The user_message tag wraps the user's request as it appears in the conversation history.",
            Section.end(),
        ]
        return list_to_multiline_text(lines)

    async def _generate_plan_section(self, state: BaseState) -> str:
        plan = state.get("plan")
        if not plan:
            return ""

        rows = "\n".join(
            f"| {step['id']} | {step['content']} | {step.get('note') or ''} | {step['status']} |"
            for step in sorted(plan, key=lambda s: s["order"])
        )

        message_parts = [
            Section.start(SectionType.PLAN),
            "| # | Task | Note | Status |",
            "|---|------|------|--------|",
            rows,
            Section.end(),
        ]

        return list_to_multiline_text(message_parts)

    async def generate_state(self, state: BaseState, extra: dict | None = {}) -> dict:
        prompt_state = {**state, **(extra or {})}

        # Create dictionary to map task names to their coroutines
        tasks = {}

        # Always executed tasks
        tasks.update(
            {
                "project_environment": self._generate_project_environment(),
                "modified_messages": self._gather_modified_messages(state),
                "commit_guidelines": self._gather_commit_guidelines(),
                "constraints": self._gather_constraints(state),
                "available_skills": self._generate_available_skills(),
                "loaded_skills": self._generate_loaded_skills(),
                "reinforcement": self._gather_reinforcement(),
                "project_context": self._gather_project_context(),
                "user_request": self._complete_user_request(state.get("user_request", "")),
                "plan": self._generate_plan_section(state),
                "preamble": self._generate_preamble(),
            }
        )

        # Handle file context tasks
        if state.get("metadata", {}).prompt_settings.has_file_context:
            tasks.update(
                {
                    "file_context": self._gather_file_context(),
                }
            )

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks.values())

        # Map results back to their keys
        results_dict = dict(zip(tasks.keys(), results))

        prompt_state.update(
            {
                "project_environment": results_dict["project_environment"],
                "modified_messages": results_dict["modified_messages"],
                "commit_guidelines": results_dict["commit_guidelines"],
                "constraints_context": results_dict["constraints"],
                "available_skills": results_dict["available_skills"],
                "loaded_skills": results_dict["loaded_skills"],
                "operating_principles": results_dict["reinforcement"],
                "project_context": results_dict["project_context"],
                "user_request": results_dict["user_request"],
                "plan": results_dict["plan"],
                "preamble": results_dict["preamble"],
            }
        )

        if "file_context" in results_dict:
            prompt_state.update(
                {
                    "file_context": results_dict["file_context"],
                }
            )

        self.prompt_state = prompt_state

        return prompt_state

    async def generate_messages(self) -> dict:
        # TODO: We should make this async gather
        return {
            "system_message": self.assemble_message(self.agent_node.get_system_template()),
            "user_message": self.assemble_message(self.agent_node.get_user_template()),
            "scratch_messages": self.generate_scratch_state(),
            "context_message": self.generate_refreshed_context_state(),
        }

    def assemble_message(self, template: list[str]) -> str:
        """Replace {placeholder} tokens in template with provided values.

        Automatically removes lines containing only placeholders that don't have corresponding values.
        Placeholders are expected to be on their own line with nothing else.

        Usage: `assembler.assemble_system_message(name="World", age=30)`
        """

        result_lines = []
        placeholder_pattern = r"^\{([^}]+)\}$"

        for line in template:
            match = re.match(placeholder_pattern, line)
            if match:
                # Line contains only a placeholder
                key = match.group(1)
                if key in self.prompt_state:
                    # Replace with the value
                    value = self.prompt_state[key]
                    result_lines.append(value if isinstance(value, str) else str(value))
                # If key not in prompt_state, skip this line (remove it)
            else:
                # Not a placeholder line, keep as-is
                result_lines.append(line)

        return list_to_multiline_text(result_lines)

    def generate_refreshed_context_state(self) -> str:
        """ """
        refreshed_context_message = list_to_multiline_text(
            [
                self.prompt_state["loaded_skills"],
                self.prompt_state["project_context"],
                self.prompt_state["project_environment"],
                Section.start(SectionType.PROJECT_STATE),
                "Below is the current state of the project. It includes all your changes as a result of previous tool calls that have been masked for brevity.",
                "",
                Section.important("You MUST trust this information as the current state of the files etc."),
                "",
                self.prompt_state["file_context"],
                "",
                Section.end(),
                self.prompt_state["plan"],
                self.epilogue(),
            ]
        )

        return refreshed_context_message

    def generate_scratch_state(self) -> list[BaseMessage]:
        """ """

        return self.prompt_state.get("scratch_messages", [])

    def epilogue(self) -> str:
        history_messages = self.prompt_state.get("history_messages", [])

        lines = [
            Section.start(SectionType.RESUME_FORMAT),
            "",
        ]

        # TODO: Should we consider plan here ?
        if not history_messages:
            lines.append("> **Remember**: This is your first response so you are starting at the FIRST step.")
        else:
            lines.extend(
                [
                    f"> **Remember**: This is a followup response. Make sure to consider the {Section.ref(SectionType.WORKFLOW)} section and plan accordingly."
                ]
            )

        return list_to_multiline_text(lines)
