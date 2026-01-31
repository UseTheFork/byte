from langchain_core.prompts.chat import ChatPromptTemplate

from byte.prompt_format import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text

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
                    Boundary.critical("You MUST follow the commit guidelines provided in the Rules section below."),
                    "Read and apply ALL rules for commit types, scopes, and description formatting.",
                    "Group files logically by the nature of their changes (e.g., all files related to a single feature, bug fix, or refactor).",
                    Boundary.close(BoundaryType.TASK),
                ]
            ),
        ),
        ("placeholder", "{commit_guidelines}"),
        ("placeholder", "{masked_messages}"),
        ("user", "{processed_user_request}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
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
                    "You are an expert software engineer that generates concise, Git commit messages based on the provided diffs.",
                    "Review the provided context and diffs which are about to be committed to a git repo.",
                    "Review the diffs carefully.",
                    Boundary.critical("You MUST follow the commit guidelines provided in the Rules section below."),
                    "Read and apply ALL rules for commit types, scopes, and description formatting.",
                    Boundary.close(BoundaryType.TASK),
                ]
            ),
        ),
        ("placeholder", "{commit_guidelines}"),
        ("user", "{processed_user_request}"),
        ("placeholder", "{scratch_messages}"),
        ("placeholder", "{errors}"),
    ]
)

commit_enforcement = [
    "- When creating a Commit Plan, ALL provided files MUST be included in the plan. Do not omit any files from the staged changes.",
]
