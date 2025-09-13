from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class KnowledgeConfig:
    """Knowledge domain configuration for long-term memory storage."""

    database_path: Optional[str] = None  # Defaults to .byte/knowledge.db
    enable_semantic_search: bool = False  # Requires embedding model
    embedding_model: Optional[str] = None  # Model for semantic search
    max_items_per_namespace: int = 1000  # Limit items per namespace
    enable_ttl: bool = True  # Enable time-to-live for items
    default_ttl_minutes: int = 43200  # 30 days default TTL
