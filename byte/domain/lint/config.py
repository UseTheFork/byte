from typing import List

from pydantic.dataclasses import dataclass

from byte.core.config.schema import BaseConfig


@dataclass(frozen=True)
class LintConfig(BaseConfig):
    """Lint domain configuration with validation and defaults."""

    enabled: bool = True
    commands: List[str] | None = None
