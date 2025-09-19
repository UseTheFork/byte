from typing import Any, Dict, List, Optional

from byte.core.service.mixins import Bootable, Injectable
from byte.domain.events.mixins import Eventable
from byte.domain.knowledge.models import KnowledgeItem, ProjectPattern, UserPreference
from byte.domain.knowledge.store import ByteKnowledgeStore


class KnowledgeService(Eventable, Injectable, Bootable):
    """Domain service for long-term knowledge and preference management.

    Orchestrates persistent storage of user preferences, project patterns,
    and learned behaviors across conversation sessions. Provides high-level
    APIs for storing and retrieving knowledge with semantic organization.
    Usage: `knowledge_service.set_user_preference("theme", "dark")` -> persists preference
    """

    async def boot(self) -> None:
        self._store: Optional[ByteKnowledgeStore] = None

    @property
    async def store(self) -> ByteKnowledgeStore:
        """Get knowledge store with lazy initialization.

        Usage: `store = knowledge_service.store` -> direct store access
        """
        if self._store is None:
            config_service = await self.make("config")
            self._store = ByteKnowledgeStore(config_service)
        return self._store

    async def set_user_preference(
        self, category: str, subcategory: str, settings: Dict[str, Any]
    ) -> bool:
        """Store user preference with hierarchical organization.

        Usage: `await knowledge_service.set_user_preference("coding", "python", {"indent": 4})`
        """
        preference = UserPreference(category, subcategory, settings)
        item = KnowledgeItem(
            namespace=["user", "preferences", category],
            key=subcategory,
            value=preference.settings,
            metadata={"type": "user_preference", "category": category},
        )

        store = await self.store
        return await store.put(item)

    async def get_user_preference(
        self, category: str, subcategory: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve user preference settings.

        Usage: `settings = await knowledge_service.get_user_preference("coding", "python")`
        """
        item = await self.store.get(["user", "preferences", category], subcategory)
        return item.value if item else None

    async def set_project_pattern(
        self, pattern_type: str, pattern_data: Dict[str, Any], confidence: float = 1.0
    ) -> bool:
        """Store project-specific learned pattern.

        Usage: `await knowledge_service.set_project_pattern("file_structure", {"dirs": ["src"]})`
        """
        project_root = self.config.app.project_root.name
        pattern = ProjectPattern(pattern_type, pattern_data, confidence)
        item = KnowledgeItem(
            namespace=["project", project_root, "patterns"],
            key=pattern_type,
            value={"data": pattern.pattern_data, "confidence": pattern.confidence},
            metadata={"type": "project_pattern", "project": project_root},
        )
        return await self.store.put(item)

    async def get_project_pattern(self, pattern_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve project-specific pattern.

        Usage: `pattern = await knowledge_service.get_project_pattern("file_structure")`
        """
        project_root = self.config.app.project_root.name
        item = await self.store.get(["project", project_root, "patterns"], pattern_type)
        return item.value if item else None

    async def store_knowledge(
        self,
        namespace: List[str],
        key: str,
        value: Any,
        ttl_minutes: Optional[int] = None,
    ) -> bool:
        """Store arbitrary knowledge with custom namespace.

        Usage: `await knowledge_service.store_knowledge(["ai", "learned"], "pattern", data)`
        """
        item = KnowledgeItem(
            namespace=namespace,
            key=key,
            value=value,
            ttl_minutes=ttl_minutes,
            metadata={"type": "custom_knowledge"},
        )
        return await self.store.put(item)

    async def retrieve_knowledge(self, namespace: List[str], key: str) -> Optional[Any]:
        """Retrieve knowledge by namespace and key.

        Usage: `data = await knowledge_service.retrieve_knowledge(["ai", "learned"], "pattern")`
        """
        item = await self.store.get(namespace, key)
        return item.value if item else None

    async def search_knowledge(
        self, namespace_prefix: List[str], limit: int = 50
    ) -> List[KnowledgeItem]:
        """Search knowledge within namespace hierarchy.

        Usage: `items = await knowledge_service.search_knowledge(["user"])` -> all user knowledge
        """
        return await self.store.search(namespace_prefix, limit)

    async def get_user_preferences_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all user preferences organized by category.

        Usage: `prefs = await knowledge_service.get_user_preferences_summary()` -> all preferences
        """
        items = await self.store.search(["user", "preferences"])
        summary = {}

        for item in items:
            if len(item.namespace) >= 3:
                category = item.namespace[2]  # ["user", "preferences", "category"]
                if category not in summary:
                    summary[category] = {}
                summary[category][item.key] = item.value

        return summary

    async def cleanup_expired_knowledge(self) -> int:
        """Remove expired knowledge items based on TTL.

        Usage: `count = await knowledge_service.cleanup_expired_knowledge()` -> maintenance
        """
        return await self.store.cleanup_expired()

    async def close(self):
        """Close knowledge service resources."""
        if self._store:
            await self._store.close()
