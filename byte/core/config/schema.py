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
    has_git: bool = False


@dataclass(frozen=True)
class LLMConfig:
    """Language model configuration."""

    provider: str = "auto"
    model: str = "main"
    temperature: float = 0.1
    max_tokens: Optional[int] = None


@dataclass(frozen=True)
class CommitConfig:
    """Git commit configuration."""

    custom_prompt: Optional[str] = None
    auto_commits: bool = False


@dataclass(frozen=True)
class UIConfig:
    """User interface configuration."""

    theme: str = "dark"
    show_file_context: bool = True
    code_theme: str = "default"
    dark_mode: bool = True


@dataclass(frozen=True)
class Config:
    """Root configuration object containing all config sections."""

    app: AppConfig
    llm: LLMConfig
    commit: CommitConfig
    ui: UIConfig

    @classmethod
    def from_dict(cls, data: dict, project_root: Path, has_git: bool) -> "Config":
        """Create Config from dictionary with flexible YAML mapping."""

        # Use get() with sensible defaults for all values
        app_data = data.get("app", {})
        llm_data = data.get("llm", {})

        # Custom mappings for UI
        ui_data = {
            "theme": data.get("ui", {}).get("theme", "dark"),
            "show_file_context": data.get("ui", {}).get("show_file_context", True),
            "code_theme": data.get("code-theme", "default"),
            "dark_mode": data.get("dark-mode", True),
        }

        # Custom mappings for commit
        commit_data = {
            "custom_prompt": data.get("commit", {}).get("prompt"),
            "auto_commits": data.get("auto-commits", False),
        }

        return cls(
            app=AppConfig(
                name=app_data.get("name", "Byte"),
                version=app_data.get("version", "1.0.0"),
                debug=app_data.get("debug", False),
                project_root=project_root,
                has_git=has_git,
            ),
            llm=LLMConfig(**{k: v for k, v in llm_data.items() if v is not None}),
            commit=CommitConfig(
                **{k: v for k, v in commit_data.items() if v is not None}
            ),
            ui=UIConfig(**{k: v for k, v in ui_data.items() if v is not None}),
        )
