import json
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

import aiosqlite

from byte.domain.knowledge.models import KnowledgeItem

if TYPE_CHECKING:
    from byte.core.config.service import ConfigService


class ByteKnowledgeStore:
    """Async SQLite-based knowledge store for long-term memory persistence.

    Implements hierarchical namespace storage with optional semantic search
    capabilities. Provides efficient async storage and retrieval of user preferences,
    project patterns, and learned behaviors across conversation sessions.
    Usage: `store = ByteKnowledgeStore(config_service)` -> knowledge persistence
    """

    def __init__(self, config_service: "ConfigService"):
        self.config_service = config_service
        self._conn: Optional[aiosqlite.Connection] = None

    async def get_connection(self) -> aiosqlite.Connection:
        """Get database connection with lazy initialization.

        Usage: `conn = await store.get_connection()` -> ready for queries
        """
        if self._conn is None:
            self._conn = await self._create_connection()
        return self._conn

    async def _create_connection(self) -> aiosqlite.Connection:
        """Create and configure async SQLite connection with schema setup."""
        # Get database path from config or use default
        knowledge_config = self.config_service.config.knowledge
        if knowledge_config.database_path:
            db_path = Path(knowledge_config.database_path)
        else:
            db_path = self.config_service.byte_dir / "knowledge.db"

        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create async connection
        conn = await aiosqlite.connect(str(db_path))

        # Enable foreign keys and WAL mode for better performance
        await conn.execute("PRAGMA foreign_keys = ON")
        await conn.execute("PRAGMA journal_mode = WAL")

        # Setup schema
        await self._setup_schema(conn)

        return conn

    async def _setup_schema(self, conn: aiosqlite.Connection) -> None:
        """Initialize database schema for knowledge storage."""
        await conn.executescript(
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
        await conn.commit()

    async def put(self, item: KnowledgeItem) -> bool:
        """Store or update a knowledge item.

        Usage: `success = await store.put(knowledge_item)` -> persists item
        """
        try:
            conn = await self.get_connection()
            namespace_str = "/".join(item.namespace)
            value_json = json.dumps(item.value)
            metadata_json = json.dumps(item.metadata) if item.metadata else None

            # Calculate expiration if TTL is set
            expires_at = None
            if item.ttl_minutes:
                expires_at = f"datetime('now', '+{item.ttl_minutes} minutes')"

            await conn.execute(
                """
                INSERT OR REPLACE INTO knowledge_items
                (namespace, key, value, metadata, ttl_minutes, expires_at)
                VALUES (?, ?, ?, ?, ?, {})
                """.format(expires_at or "NULL"),
                (namespace_str, item.key, value_json, metadata_json, item.ttl_minutes),
            )
            await conn.commit()
            return True
        except Exception:
            return False

    async def get(self, namespace: List[str], key: str) -> Optional[KnowledgeItem]:
        """Retrieve a knowledge item by namespace and key.

        Usage: `item = await store.get(["user", "prefs"], "theme")` -> retrieves item
        """
        try:
            conn = await self.get_connection()
            namespace_str = "/".join(namespace)
            cursor = await conn.execute(
                """
                SELECT namespace, key, value, metadata, created_at, updated_at, ttl_minutes
                FROM knowledge_items
                WHERE namespace = ? AND key = ?
                AND (expires_at IS NULL OR expires_at > datetime('now'))
                """,
                (namespace_str, key),
            )

            row = await cursor.fetchone()
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

    async def search(
        self, namespace_prefix: List[str], limit: int = 50
    ) -> List[KnowledgeItem]:
        """Search for items within a namespace hierarchy.

        Usage: `items = await store.search(["user"])` -> all user items
        """
        try:
            conn = await self.get_connection()
            namespace_pattern = "/".join(namespace_prefix) + "%"
            cursor = await conn.execute(
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
            async for row in cursor:
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

    async def delete(self, namespace: List[str], key: str) -> bool:
        """Delete a knowledge item.

        Usage: `success = await store.delete(["user", "prefs"], "theme")` -> removes item
        """
        try:
            conn = await self.get_connection()
            namespace_str = "/".join(namespace)
            cursor = await conn.execute(
                "DELETE FROM knowledge_items WHERE namespace = ? AND key = ?",
                (namespace_str, key),
            )
            await conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False

    async def cleanup_expired(self) -> int:
        """Remove expired items based on TTL settings.

        Usage: `count = await store.cleanup_expired()` -> maintenance cleanup
        """
        try:
            conn = await self.get_connection()
            cursor = await conn.execute(
                "DELETE FROM knowledge_items WHERE expires_at <= datetime('now')"
            )
            await conn.commit()
            return cursor.rowcount
        except Exception:
            return 0

    async def list_namespaces(self) -> List[List[str]]:
        """List all unique namespaces in the store.

        Usage: `namespaces = await store.list_namespaces()` -> available namespaces
        """
        try:
            conn = await self.get_connection()
            cursor = await conn.execute(
                "SELECT DISTINCT namespace FROM knowledge_items ORDER BY namespace"
            )
            rows = await cursor.fetchall()
            return [row[0].split("/") for row in rows]
        except Exception:
            return []

    async def close(self):
        """Close database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None
