from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class GitConfig:
    """Git domain configuration with validation and defaults."""

    include_untracked: bool = False
    include_staged: bool = True
    include_unstaged: bool = True
