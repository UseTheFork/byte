from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CommitConfig:
    """Commit domain configuration with validation and defaults."""

    custom_prompt: Optional[str] = None
    auto_commits: bool = False
