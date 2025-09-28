from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class KnowledgeItem:
    """Represents a knowledge item with metadata and content.

    Encapsulates stored knowledge with hierarchical namespace support,
    enabling organized storage of user preferences, project patterns,
    and learned behaviors across conversation sessions.
    Usage: `KnowledgeItem(namespace=["user", "prefs"], key="theme", value="dark")`
    """

    namespace: List[
        str
    ]  # Hierarchical namespace like ["user", "project", "preferences"]
    key: str  # Unique key within namespace
    value: Any  # Stored data (can be any JSON-serializable type)
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata
    created_at: Optional[datetime] = None  # Creation timestamp
    updated_at: Optional[datetime] = None  # Last update timestamp
    ttl_minutes: Optional[int] = None  # Time-to-live in minutes


@dataclass(frozen=True)
class UserPreference:
    """User-specific preference storage model.

    Usage: `UserPreference("coding_style", "python", {"indent": 4})`
    """

    category: str  # Preference category like "coding_style", "ui_theme"
    subcategory: str  # Subcategory like "python", "javascript"
    settings: Dict[str, Any]  # Preference settings


@dataclass(frozen=True)
class ProjectPattern:
    """Project-specific learned pattern storage model.

    Usage: `ProjectPattern("file_structure", {"common_dirs": ["src", "tests"]})`
    """

    pattern_type: str  # Type of pattern like "file_structure", "naming_convention"
    pattern_data: Dict[str, Any]  # Pattern details and examples
    confidence: float = 1.0  # Confidence score for the pattern
