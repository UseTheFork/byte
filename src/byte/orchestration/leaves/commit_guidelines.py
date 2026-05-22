from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.support import MD, Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


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


class CommitGuidelines(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> str:

        config = prompt_assembler.get_app()["config"]
        commit_guidelines = []

        commit_guidelines.append(Section.start(SectionType.RULES))
        commit_guidelines.append(Section.sub_heading("Allowed Commit Types", 2, True))

        commit_types_list = "\n".join(
            MD.bullet(f"**{type_name}**: {description}") for type_name, description in COMMIT_TYPES.items()
        )
        commit_guidelines.append(commit_types_list)

        commit_guidelines.append(Section.sub_heading("Commit Description Guidelines", 2))

        description_guidelines = [
            MD.bullet("Use imperative mood (e.g., 'add feature' not 'added feature' or 'adding feature')"),
            MD.bullet("Start with lowercase letter"),
            MD.bullet("Do not end with a period"),
            MD.bullet(f"Keep under {config.git.max_description_length} characters"),
            MD.bullet("Be concise and descriptive"),
            MD.bullet("Focus on what the change does, not how it does it"),
        ]

        # Add any custom guidelines from config
        if config.git.description_guidelines:
            for guideline in config.git.description_guidelines:
                description_guidelines.append(MD.bullet(guideline))

        commit_guidelines.append("\n".join(description_guidelines))

        commit_guidelines.append(Section.sub_heading("Allowed Commit Scopes", 2))

        if config.git.enable_scopes and config.git.scopes:
            scope_list = "\n".join(MD.bullet(scope) for scope in config.git.scopes)
            commit_guidelines.append(scope_list)

        commit_guidelines.append(Section.sub_heading("Field Inclusion Rules", 2))

        field_rules = []
        if not config.git.enable_scopes:
            field_rules.append(MD.bullet("DO NOT include `scope` in the commit message"))
        if not config.git.enable_body:
            field_rules.append(MD.bullet("DO NOT include `body` in the commit message"))
        if not config.git.enable_breaking_changes:
            field_rules.append(
                MD.bullet("DO NOT include `breaking_change` or `breaking_change_message` in the commit message")
            )

        if field_rules:
            commit_guidelines.append("\n".join(field_rules))
        else:
            commit_guidelines.append(MD.bullet("All optional fields are enabled and may be included when appropriate"))

        return list_to_multiline_text(commit_guidelines)
