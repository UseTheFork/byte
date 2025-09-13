from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class AppConfig:
    """Application-level configuration."""

    name: str = "Byte"
    version: str = "1.0.0"
    debug: bool = False
    project_root: Optional[Path] = None


@dataclass(frozen=True)
class Config:
    """Root configuration object containing all config sections."""

    app: AppConfig

    def __init__(self, **kwargs):
        # Use object.__setattr__ since this is a frozen dataclass
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)
