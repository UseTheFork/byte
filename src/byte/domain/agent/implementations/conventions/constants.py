from pydantic import BaseModel


class ConventionFocus(BaseModel):
    """Configuration for a convention type's focus and output."""

    focus_message: str
    file_name: str


FOCUS_MESSAGES = {
    "Project Tooling": ConventionFocus(
        focus_message=(
            "Generate a project tooling convention focusing on: "
            "build systems and package managers (e.g., npm, composer, yarn, uv), "
            "bundlers and dev tools (e.g., vite, webpack), "
            "task runners, linting and formatting tools, "
            "and tooling configuration standards."
        ),
        file_name="PROJECT_TOOLING.md",
    ),
    "Documentation": ConventionFocus(
        focus_message=(
            "Generate a documentation convention focusing on: "
            "documentation structure and format (e.g., MkDocs), "
            "content organization, writing style and tone, "
            "code example standards, and documentation maintenance practices."
        ),
        file_name="DOCUMENTATION_STANDARDS.md",
    ),
    "Language Style Guide": ConventionFocus(
        focus_message=(
            "Generate a language style guide convention focusing on: "
            "naming conventions, code formatting, type hints, imports, "
            "class and function structure, and language-specific best practices."
        ),
        file_name="LANGUAGE_STYLE_GUIDE.md",
    ),
    "Project Architecture": ConventionFocus(
        focus_message=(
            "Generate a project architecture convention focusing on: "
            "directory structure, module organization, dependency patterns, "
            "separation of concerns, and architectural principles used in this codebase."
        ),
        file_name="PROJECT_ARCHITECTURE.md",
    ),
    "Comment Standards": ConventionFocus(
        focus_message=(
            "Generate a comment standards convention focusing on: "
            "docstring format and requirements, inline comment style, "
            "when to comment vs self-documenting code, and documentation best practices."
        ),
        file_name="COMMENT_STANDARDS.md",
    ),
    "Code Patterns": ConventionFocus(
        focus_message=(
            "Generate a code patterns convention focusing on: "
            "common design patterns used, error handling approaches, "
            "async/await patterns, dependency injection, and recurring code structures."
        ),
        file_name="CODE_PATTERNS.md",
    ),
    "Frontend Code Patterns": ConventionFocus(
        focus_message=(
            "Generate a frontend code patterns convention focusing on: "
            "component structure and organization, state management patterns, "
            "UI/UX patterns, event handling, API integration patterns, "
            "and frontend-specific design patterns."
        ),
        file_name="FRONTEND_CODE_PATTERNS.md",
    ),
    "Backend Code Patterns": ConventionFocus(
        focus_message=(
            "Generate a backend code patterns convention focusing on: "
            "API design patterns, database access patterns, service layer organization, "
            "authentication and authorization patterns, error handling and logging, "
            "and backend-specific architectural patterns."
        ),
        file_name="BACKEND_CODE_PATTERNS.md",
    ),
    "Testing Code Patterns": ConventionFocus(
        focus_message=(
            "Generate a testing code patterns convention focusing on: "
            "test structure and organization, testing frameworks and tools, "
            "unit test patterns, integration test patterns, mocking and fixtures, "
            "test naming conventions, and testing best practices."
        ),
        file_name="TESTING_CODE_PATTERNS.md",
    ),
}
