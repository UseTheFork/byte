from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class CodeBlock:
    """Code block extracted from AI messages for clipboard operations.

    Stores language identifier and content for syntax-highlighted display and copying.

    Usage: `block = CodeBlock(language="python", content="print('hello')")`
    """

    language: str = Field(description="Programming language identifier (e.g., 'python', 'javascript')")
    content: str = Field(description="Raw code content without markdown delimiters")
