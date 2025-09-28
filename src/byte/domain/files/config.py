from byte.core.config.config import BaseConfig


class FileWatchConfig(BaseConfig):
    """Configuration for file watching functionality."""

    enabled: bool = True
    ai_comment_patterns: bool = True
    debounce_ms: int = 500
    auto_add_on_ai_comment: bool = True
    auto_trigger_completion: bool = False


class FilesConfig(BaseConfig):
    """Configuration for file management functionality."""

    watch: FileWatchConfig = FileWatchConfig()
