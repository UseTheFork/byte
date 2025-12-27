from langchain_core.prompts.chat import ChatPromptTemplate

from byte.core.utils.list_to_multiline_text import list_to_multiline_text
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary

detailed_commit_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
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
                    "Use these for [type]: fix, feat, build, chore, ci, docs, style, refactor, perf, test",
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
                    "Use these for [type]: fix, feat, build, chore, ci, docs, style, refactor, perf, test",
                    "Ensure the commit message:",
                    "- Starts with the appropriate prefix.",
                    '- Is in the imperative mood (e.g., "add feature" not "added feature" or "adding feature").',
                    "- Does not exceed 72 characters.",
                    "Reply only with the one-line commit message, without any additional text, explanations, or line breaks.",
                    Boundary.close(BoundaryType.TASK),
                ]
            ),
        ),
        ("user", "{processed_user_request}"),
        ("placeholder", "{scratch_messages}"),
    ]
)
