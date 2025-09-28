from typing import List

from byte.core.config.config import BaseConfig


class LintConfig(BaseConfig):
    """Lint domain configuration with validation and defaults."""

    enabled: bool = True
    commands: List[str] | None = None
