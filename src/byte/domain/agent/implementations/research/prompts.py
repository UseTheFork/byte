from textwrap import dedent

from langchain_core.prompts import ChatPromptTemplate

research_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            dedent("""
            # Task
            Analyze this codebase to create a:

            ## COMMENT_STYLEGUIDE.md containing:
            - Comment formatting rules (placement, capitalization, punctuation)
            - Guidelines for explaining "why" not "what" with examples
            - Function/method documentation patterns with type hints and usage examples
            - Special tags (TODO, FIXME, NOTE) and their appropriate usage
            - Make this file about 20-30 lines long.

            ## [language]_STYLEGUIDE.md containing:
            - Code style guidelines including imports, formatting, types, naming conventions, error handling, etc.
            - Common patterns and idioms observed in the codebase
            - Class design principles (inheritance, composition, abstractions)
            - Project-specific conventions for file organization and module structure
            - Make this file about 20-30 lines long.

            ## PROJECT_TOOLING.md containing:
            - Build system configuration (e.g., pyproject.toml, package.json, vite.config.js)
            - Key dependencies and their purposes
            - Environment setup requirements and toolchain versions
            - Make this file about 20-30 lines long.

            # Guidelines
            - The files you create will be given to agentic coding agents (such as yourself) that operate in this repository. Make each file about 20-30 lines long.
            - Only make one tool call at a time.
            - **You have at most 10 tool calls to do this task.**

            # Output Requirements
            When you are ready output all three files as markdown blocks.
            """),
        ),
        ("placeholder", "{messages}"),
        ("placeholder", "{errors}"),
    ]
)
