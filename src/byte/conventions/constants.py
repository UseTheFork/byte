from pydantic import BaseModel


class ConventionFocus(BaseModel):
    """Configuration for a convention type's focus and output."""

    focus_message: str
    requires_user_input: bool


FOCUS_MESSAGES = {
    # keep-sorted start block=yes
    "Backend Code Patterns": ConventionFocus(
        focus_message=(
            "Generate a backend code patterns convention focusing on: "
            "API design patterns, database access patterns, service layer organization, "
            "authentication and authorization patterns, error handling and logging, "
            "and backend-specific architectural patterns."
        ),
        requires_user_input=False,
    ),
    "Code Patterns": ConventionFocus(
        focus_message=(
            "Generate a code patterns convention focusing on: "
            "common design patterns used, error handling approaches, "
            "async/await patterns, dependency injection, and recurring code structures."
        ),
        requires_user_input=False,
    ),
    "Comment Standards": ConventionFocus(
        focus_message=(
            "Generate a comment standards convention focusing on: "
            "docstring format and requirements, inline comment style, "
            "when to comment vs self-documenting code, and documentation best practices."
        ),
        requires_user_input=False,
    ),
    "Documentation": ConventionFocus(
        focus_message=(
            "Generate a documentation convention focusing on: "
            "documentation structure and format (e.g., MkDocs), "
            "content organization, writing style and tone, "
            "code example standards, and documentation maintenance practices."
        ),
        requires_user_input=False,
    ),
    "Domain Documentation": ConventionFocus(
        focus_message=(
            "Generate domain-specific documentation focusing on: "
            "domain purpose and responsibilities, key components and their interactions, "
            "data models and business logic, API contracts and interfaces, "
            "domain-specific patterns and conventions, and integration points with other domains. "
            "Focus on the following domain:"
        ),
        requires_user_input=True,
    ),
    "Frontend Code Patterns": ConventionFocus(
        focus_message=(
            "Generate a frontend code patterns convention focusing on: "
            "component structure and organization, state management patterns, "
            "UI/UX patterns, event handling, API integration patterns, "
            "and frontend-specific design patterns."
        ),
        requires_user_input=False,
    ),
    "Language Style Guide": ConventionFocus(
        focus_message=(
            "Generate a language style guide convention focusing on: "
            "naming conventions, code formatting, type hints, imports, "
            "class and function structure, and language-specific best practices."
        ),
        requires_user_input=False,
    ),
    "Project Architecture": ConventionFocus(
        focus_message=(
            "Generate a project architecture convention focusing on: "
            "directory structure, module organization, dependency patterns, "
            "separation of concerns, and architectural principles used in this codebase."
        ),
        requires_user_input=False,
    ),
    "Project Tooling": ConventionFocus(
        focus_message=(
            "Generate a project tooling convention focusing on: "
            "build systems and package managers (e.g., npm, composer, yarn, uv), "
            "bundlers and dev tools (e.g., vite, webpack), "
            "task runners, linting and formatting tools, "
            "and tooling configuration standards."
        ),
        requires_user_input=False,
    ),
    "Testing Code Patterns": ConventionFocus(
        focus_message=(
            "Generate a testing code patterns convention focusing on: "
            "test structure and organization, testing frameworks and tools, "
            "unit test patterns, integration test patterns, mocking and fixtures, "
            "test naming conventions, and testing best practices."
        ),
        requires_user_input=False,
    ),
    # keep-sorted end
    "Other": ConventionFocus(
        focus_message=(""),
        requires_user_input=True,
    ),
}
