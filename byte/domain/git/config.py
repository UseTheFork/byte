from typing import Optional

from byte.core.config.config import BaseConfig


class CoderConfig(BaseConfig):
    """Coder agent configuration for specialized coding assistance."""

    project_root: Optional[str] = ""  # Maximum tool-calling iterations
    max_iterations: int = 10  # Maximum tool-calling iterations
    interrupt_before_tools: bool = False  # Interrupt before tool execution
    system_prompt: Optional[str] = None  # Custom system prompt override
    temperature: float = 0.1  # Lower temperature for more focused code generation
