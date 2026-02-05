from byte import Service
from byte.git import CommitGroup, CommitMessage, CommitPlan, GitService
from byte.support import Boundary, BoundaryType
from byte.support.mixins import UserInteractive
from byte.support.utils import list_to_multiline_text

# Credits to https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13
COMMIT_TYPES = {
    "feat": "Commits that add or remove a new feature to the API or UI",
    "fix": "Commits that fix an API or UI bug of a preceded feat commit",
    "refactor": "Commits that rewrite/restructure code without changing API or UI behaviour",
    "perf": "Commits that improve performance (special refactor commits)",
    "style": "Commits that do not affect meaning (white-space, formatting, missing semi-colons, etc)",
    "test": "Commits that add missing tests or correct existing tests",
    "build": "Commits that affect build components (build tool, CI pipeline, dependencies, project version, etc)",
    "ops": "Commits that affect operational components (infrastructure, deployment, backup, recovery, etc)",
    "docs": "Commits that affect documentation only",
    "chore": "Commits that represent tasks (initial commit, modifying .gitignore, etc)",
}


class CommitService(Service, UserInteractive):
    """Service for handling git commit operations and formatting.

    Provides utilities for formatting commit messages according to conventional
    commit standards and managing the commit workflow.
    """

    def boot(self, *args, **kwargs) -> None:
        self.git_service = self.app.make(GitService)

    async def build_commit_prompt(self) -> str:
        """Build a formatted prompt from staged changes for AI commit message generation.

        Extracts the staged diff, formats it with boundaries for each file, and creates
        a structured prompt containing both diff content and file change summaries.

        Returns:
            Formatted prompt string ready for AI processing

        Usage: `prompt = await self.build_commit_prompt()`
        """
        # Extract staged changes for AI analysis
        staged_diff = await self.git_service.get_diff()

        # Build formatted diff sections for each file
        diff_section = []
        file_section = [Boundary.open(BoundaryType.CONTEXT, meta={"type": "Files"})]
        for diff_item in staged_diff:
            msg = diff_item["msg"]
            file_path = diff_item["file"]
            change_type = diff_item["change_type"]

            # Start file section with change type
            diff_section.append(
                Boundary.open(
                    BoundaryType.CONTEXT,
                    meta={"type": "Diff", "change_type": change_type, "file": file_path},
                )
            )
            file_section.append(f"{msg}")

            # Include diff content only for non-deleted files
            if change_type != "D" and diff_item["diff"]:
                diff_section.append(diff_item["diff"])

            diff_section.append(Boundary.close(BoundaryType.CONTEXT))

        file_section.append(Boundary.close(BoundaryType.CONTEXT))
        prompt = list_to_multiline_text(diff_section) + list_to_multiline_text(file_section)
        return prompt

    async def process_commit_plan(self, commit_plan: CommitPlan) -> None:
        """Process the commit plan by unstaging all files and committing each group separately.

        Unstages all currently staged files, then iterates through each commit group
        in the plan, staging only the files for that group and creating a commit with
        the group's message.

        Args:
            commit_plan: The CommitPlan containing commit groups with messages and files

        Usage: `await self.process_commit_plan(commit_plan)`
        """

        # Unstage all files
        await self.git_service.reset()

        # Iterate over each commit group
        for commit_group in commit_plan.commits:
            # Stage files for this commit group
            for file_path in commit_group.files:
                file_full_path = self.app.root_path(file_path)
                if file_full_path.exists():
                    await self.git_service.add(file_path)
                else:
                    # File was deleted, stage the deletion
                    await self.git_service.remove(file_path)

            # Commit with the group's message
            formatted_message = await self.format_conventional_commit(commit_group)
            await self.git_service.commit(formatted_message)

    async def format_conventional_commit(self, commit_message: CommitMessage | CommitGroup) -> str:
        """Format a CommitMessage into a conventional commit string.

        Formats according to the Conventional Commits specification:
        <type>[optional scope][!]: <description>

        [optional body]

        Respects GitConfig settings for scopes, breaking changes, and body inclusion.

        Args:
            commit_message: CommitMessage object to format

        Returns:
            Formatted conventional commit message string

        Usage: `formatted = await self.format_conventional_commit(commit_message)`
        """
        git_config = self.app["config"].git

        # Build the header line
        header_parts = [commit_message.type]

        # Only add scope if enabled in config AND present in message
        if git_config.enable_scopes and commit_message.scope:
            header_parts.append(f"({commit_message.scope})")

        # Normalize the commit message: lowercase first char, remove trailing period
        description = commit_message.commit_message
        description = description[0].lower() + description[1:] if description else description
        description = description.rstrip(".")

        # Prepare message parts list for later assembly
        message_parts = []
        breaking_change_footer = None

        # Only handle breaking changes if enabled in config
        if git_config.enable_breaking_changes and commit_message.breaking_change:
            console = self.app["console"]

            # Display commit message parts for context
            context_parts = [
                f"Type: {commit_message.type}",
                f"Message: {commit_message.commit_message}",
            ]

            # Only show scope if it's enabled and present
            if git_config.enable_scopes and commit_message.scope:
                context_parts.insert(1, f"Scope: {commit_message.scope}")

            # Only show body if it's enabled and present
            if git_config.enable_body and commit_message.body:
                context_parts.append(f"Body: {commit_message.body}")

            if hasattr(commit_message, "files") and commit_message.files:
                context_parts.append(f"Files: {', '.join(commit_message.files)}")

            console.print_panel("\n".join(context_parts), title="Commit Details")

            confirmed = await self.prompt_for_confirmation(
                "This commit is marked as a breaking change. Confirm?", default=True
            )

            if confirmed:
                header_parts.append("!")

                # Add breaking change footer if message is present
                if commit_message.breaking_change_message:
                    breaking_change_footer = f"BREAKING CHANGE: {commit_message.breaking_change_message}"

        # Assemble header after breaking change confirmation
        header = "".join(header_parts) + f": {description}"

        # Build the full message
        message_parts.append(header)

        # Only add body if enabled in config AND present in message
        if git_config.enable_body and commit_message.body:
            message_parts.extend(["", commit_message.body])

        # Add breaking change footer if present
        if breaking_change_footer:
            message_parts.extend(["", breaking_change_footer])

        return "\n".join(message_parts)

    async def generate_commit_guidelines(self) -> str:
        config = self.app["config"]
        commit_guidelines = []

        commit_guidelines.append(
            Boundary.open(
                BoundaryType.RULES,
                meta={
                    "type": "Allowed Commit Types",
                },
            )
        )

        commit_types_list = "\n".join(
            f"- **{type_name}**: {description}" for type_name, description in COMMIT_TYPES.items()
        )
        commit_guidelines.append(commit_types_list)

        commit_guidelines.append(Boundary.close(BoundaryType.RULES))

        commit_guidelines.append(
            Boundary.open(
                BoundaryType.RULES,
                meta={
                    "type": "Commit Description Guidelines",
                },
            )
        )

        description_guidelines = [
            "- Use imperative mood (e.g., 'add feature' not 'added feature' or 'adding feature')",
            "- Start with lowercase letter",
            "- Do not end with a period",
            f"- Keep under {config.git.max_description_length} characters",
            "- Be concise and descriptive",
            "- Focus on what the change does, not how it does it",
        ]

        # Add any custom guidelines from config
        if config.git.description_guidelines:
            for guideline in config.git.description_guidelines:
                description_guidelines.append(f"- {guideline}")

        commit_guidelines.append("\n".join(description_guidelines))

        commit_guidelines.append(Boundary.close(BoundaryType.RULES))

        commit_guidelines.append(
            Boundary.open(
                BoundaryType.RULES,
                meta={
                    "type": "Allowed Commit Scopes",
                },
            )
        )

        if config.git.enable_scopes and config.git.scopes:
            scope_list = "\n".join(f"- {scope}" for scope in config.git.scopes)
            commit_guidelines.append(scope_list)

        commit_guidelines.append(Boundary.close(BoundaryType.RULES))

        commit_guidelines.append(
            Boundary.open(
                BoundaryType.RULES,
                meta={
                    "type": "Field Inclusion Rules",
                },
            )
        )

        field_rules = []
        if not config.git.enable_scopes:
            field_rules.append("- DO NOT include `scope` in the commit message")
        if not config.git.enable_body:
            field_rules.append("- DO NOT include `body` in the commit message")
        if not config.git.enable_breaking_changes:
            field_rules.append("- DO NOT include `breaking_change` or `breaking_change_message` in the commit message")

        if field_rules:
            commit_guidelines.append("\n".join(field_rules))
        else:
            commit_guidelines.append("- All optional fields are enabled and may be included when appropriate")

        commit_guidelines.append(Boundary.close(BoundaryType.RULES))

        return list_to_multiline_text(commit_guidelines)
