from langchain_core.prompts.chat import ChatPromptTemplate

from byte.core.utils import list_to_multiline_text
from byte.domain.agent.implementations.commit.constants import COMMIT_TYPES
from byte.domain.prompt_format import Boundary, BoundaryType

# Credits to https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13


def _format_commit_types() -> str:
    """Format COMMIT_TYPES dictionary into a readable string for prompts."""
    return "\n".join(f"  - {type_}: {description}" for type_, description in COMMIT_TYPES.items())


commit_plan_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.TASK),
                    "You are an expert software engineer that generates organized Git commits based on the provided staged files and diffs.",
                    "Review the staged files and diffs which are about to be committed to a git repo.",
                    "Review the diffs carefully and group related changes together.",
                    "Generate a list of commit groups, where each group contains:",
                    "- A concise, one-line commit message for that group of changes",
                    "- A list of file paths that belong to that commit",
                    "The commit message should be structured as follows: [type]: [description]",
                    f"Available commit types:\n{_format_commit_types()}",
                    "Ensure each commit message:",
                    "- Starts with the appropriate prefix.",
                    '- Is in the imperative mood (e.g., "add feature" not "added feature" or "adding feature").',
                    "- Does not exceed 72 characters.",
                    "Group files logically by the nature of their changes (e.g., all files related to a single feature, bug fix, or refactor).",
                    Boundary.close(BoundaryType.TASK),
                ]
            ),
        ),
        ("placeholder", "{masked_messages}"),
        ("user", "{processed_user_request}"),
        ("placeholder", "{scratch_messages}"),
    ]
)

# Conventional commit message generation prompt
# Adapted from Aider: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/prompts.py#L8
# Conventional Commits specification: https://www.conventionalcommits.org/en/v1.0.0/#summary

commit_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            list_to_multiline_text(
                [
                    Boundary.open(BoundaryType.TASK),
                    "You are an expert software engineer that generates concise, one-line Git commit messages based on the provided diffs.",
                    "Review the provided context and diffs which are about to be committed to a git repo.",
                    "Review the diffs carefully.",
                    "Generate a one-line commit message for those changes.",
                    "The commit message should be structured as follows: [type]: [description]",
                    f"Available commit types:\n{_format_commit_types()}",
                    "Ensure the commit message:",
                    "- Starts with the appropriate prefix.",
                    '- Is in the imperative mood (e.g., "add feature" not "added feature" or "adding feature").',
                    "- Does not exceed 72 characters.",
                    Boundary.close(BoundaryType.TASK),
                ]
            ),
        ),
        ("user", "{processed_user_request}"),
        ("placeholder", "{scratch_messages}"),
    ]
)
