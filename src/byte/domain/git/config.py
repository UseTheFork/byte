from typing import List

from pydantic import BaseModel, Field


class GitConfig(BaseModel):
    """Configuration for git domain operations and conventional commit behavior.

    Controls features like scope selection, breaking change detection, and commit
    message body generation for AI-powered git commits.
    """

    enable_scopes: bool = Field(
        default=False,
        description="Enable scope selection for conventional commits",
    )
    enable_breaking_changes: bool = Field(
        default=True,
        description="Enable breaking change detection and confirmation",
    )
    enable_body: bool = Field(
        default=True,
        description="Enable commit message body generation",
    )
    scopes: List[str] = Field(
        default_factory=lambda: [
            "api",
            "auth",
            "cli",
            "config",
            "core",
            "db",
            "deps",
            "docs",
            "test",
            "ui",
        ],
        description="Available scopes for conventional commits",
    )
