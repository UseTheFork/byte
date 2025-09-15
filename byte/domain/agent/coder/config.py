from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CoderConfig:
    """Coder agent configuration for specialized coding assistance."""

    max_iterations: int = 10  # Maximum tool-calling iterations
    interrupt_before_tools: bool = False  # Interrupt before tool execution
    system_prompt: Optional[str] = None  # Custom system prompt override
    temperature: float = 0.1  # Lower temperature for more focused code generation
