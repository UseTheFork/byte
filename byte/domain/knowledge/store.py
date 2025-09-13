import json
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from byte.domain.knowledge.models import KnowledgeItem

if TYPE_CHECKING:
    from byte.core.config.service import ConfigService


class ByteKnowledgeStore:
    """SQLite-based knowledge store for long-term memory persistence.

    Implements hierarchical namespace storage with optional semantic search
    capabilities. Provides efficient storage and retrieval of user preferences,
    project patterns, and learned behaviors across conversation sessions.
    Usage: `store = ByteKnowledgeStore(config_service)` -> knowledge persistence
    """

    def __init__(self, config_service: "ConfigService"):
        self.config_service = config_service
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def connection(self) -> sqlite3.Connection:
        """Get database connection with lazy initialization.

        Usage: `conn = store.connection` -> ready for queries
        """
        if self._conn is None:
            self._conn = self._create_connection()
        return self._conn

    def _create_connection(self) -> sqlite3.Connection:
        """Create and configure SQLite connection with schema setup."""
        # Get database path from config or use default
        knowledge_config = self.config_service.config.knowledge
        if knowledge_config.database_path:
            db_path = Path(knowledge_config.database_path)
        else:
            db_path = self.config_service.byte_dir / "knowledge.db"

        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create connection with optimizations
        conn = sqlite3.connect(
            str(db_path),
            check_same_thread=False,
            timeout=30.0,
        )

        # Enable foreign keys and WAL mode for better performance
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")

        # Setup schema
        self._setup_schema(conn)

        return conn

    def _setup_schema(self, conn: sqlite3.Connection) -> None:
        """Initialize database schema for knowledge storage."""
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                namespace TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ttl_minutes INTEGER,
                expires_at TIMESTAMP,
                UNIQUE(namespace, key)
            );

            CREATE INDEX IF NOT EXISTS idx_namespace ON knowledge_items(namespace);
            CREATE INDEX IF NOT EXISTS idx_key ON knowledge_items(key);
            CREATE INDEX IF NOT EXISTS idx_expires_at ON knowledge_items(expires_at);

            -- Trigger to update updated_at timestamp
            CREATE TRIGGER IF NOT EXISTS update_knowledge_items_updated_at
                AFTER UPDATE ON knowledge_items
            BEGIN
                UPDATE knowledge_items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        """
        )
        conn.commit()

    def put(self, item: KnowledgeItem) -> bool:
        """Store or update a knowledge item.

        Usage: `success = store.put(knowledge_item)` -> persists item
        """
        try:
            namespace_str = "/".join(item.namespace)
            value_json = json.dumps(item.value)
            metadata_json = json.dumps(item.metadata) if item.metadata else None

            # Calculate expiration if TTL is set
            expires_at = None
            if item.ttl_minutes:
                expires_at = f"datetime('now', '+{item.ttl_minutes} minutes')"

            self.connection.execute(
                """
                INSERT OR REPLACE INTO knowledge_items
                (namespace, key, value, metadata, ttl_minutes, expires_at)
                VALUES (?, ?, ?, ?, ?, {})
                """.format(expires_at or "NULL"),
                (namespace_str, item.key, value_json, metadata_json, item.ttl_minutes),
            )
            self.connection.commit()
            return True
        except Exception:
            return False

    def get(self, namespace: List[str], key: str) -> Optional[KnowledgeItem]:
        """Retrieve a knowledge item by namespace and key.

        Usage: `item = store.get(["user", "prefs"], "theme")` -> retrieves item
        """
        try:
            namespace_str = "/".join(namespace)
            cursor = self.connection.execute(
                """
                SELECT namespace, key, value, metadata, created_at, updated_at, ttl_minutes
                FROM knowledge_items
                WHERE namespace = ? AND key = ?
                AND (expires_at IS NULL OR expires_at > datetime('now'))
                """,
                (namespace_str, key),
            )

            row = cursor.fetchone()
            if not row:
                return None

            return KnowledgeItem(
                namespace=row[0].split("/"),
                key=row[1],
                value=json.loads(row[2]),
                metadata=json.loads(row[3]) if row[3] else None,
                created_at=row[4],
                updated_at=row[5],
                ttl_minutes=row[6],
            )
        except Exception:
            return None

    def search(
        self, namespace_prefix: List[str], limit: int = 50
    ) -> List[KnowledgeItem]:
        """Search for items within a namespace hierarchy.

        Usage: `items = store.search(["user"])` -> all user items
        """
        try:
            namespace_pattern = "/".join(namespace_prefix) + "%"
            cursor = self.connection.execute(
                """
                SELECT namespace, key, value, metadata, created_at, updated_at, ttl_minutes
                FROM knowledge_items
                WHERE namespace LIKE ?
                AND (expires_at IS NULL OR expires_at > datetime('now'))
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (namespace_pattern, limit),
            )

            items = []
            for row in cursor.fetchall():
                items.append(
                    KnowledgeItem(
                        namespace=row[0].split("/"),
                        key=row[1],
                        value=json.loads(row[2]),
                        metadata=json.loads(row[3]) if row[3] else None,
                        created_at=row[4],
                        updated_at=row[5],
                        ttl_minutes=row[6],
                    )
                )
            return items
        except Exception:
            return []

    def delete(self, namespace: List[str], key: str) -> bool:
        """Delete a knowledge item.

        Usage: `success = store.delete(["user", "prefs"], "theme")` -> removes item
        """
        try:
            namespace_str = "/".join(namespace)
            cursor = self.connection.execute(
                "DELETE FROM knowledge_items WHERE namespace = ? AND key = ?",
                (namespace_str, key),
            )
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception:
            return False

    def cleanup_expired(self) -> int:
        """Remove expired items based on TTL settings.

        Usage: `count = store.cleanup_expired()` -> maintenance cleanup
        """
        try:
            cursor = self.connection.execute(
                "DELETE FROM knowledge_items WHERE expires_at <= datetime('now')"
            )
            self.connection.commit()
            return cursor.rowcount
        except Exception:
            return 0

    def list_namespaces(self) -> List[List[str]]:
        """List all unique namespaces in the store.

        Usage: `namespaces = store.list_namespaces()` -> available namespaces
        """
        try:
            cursor = self.connection.execute(
                "SELECT DISTINCT namespace FROM knowledge_items ORDER BY namespace"
            )
            return [row[0].split("/") for row in cursor.fetchall()]
        except Exception:
            return []
