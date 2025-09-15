from pathlib import Path
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from byte.domain.agent.coder.config import CoderConfig
    from byte.domain.commit.config import CommitConfig
    from byte.domain.knowledge.config import KnowledgeConfig
    from byte.domain.memory.config import MemoryConfig


class BaseConfig(BaseModel):
    """Base configuration class that all domain configs should extend.

    Provides pydantic-based validation and serialization for all configuration
    objects in the system. Ensures consistent behavior across domains.
    Usage: `class MyDomainConfig(BaseConfig): enabled: bool = True`
    """

    pass


class AppConfig(BaseConfig):
    """Application-level configuration."""

    name: str = "Byte"
    version: str = "1.0.0"
    debug: bool = False
    project_root: Optional[Path] = None


class Config:
    """Root configuration object containing all config sections."""

    app: AppConfig

    # Type hints for dynamically added domain configs
    if TYPE_CHECKING:
        coder: "CoderConfig"
        memory: "MemoryConfig"
        knowledge: "KnowledgeConfig"
        commit: "CommitConfig"

    def __init__(self, **kwargs):
        # Use object.__setattr__ since this is a frozen dataclass
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)
