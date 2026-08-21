"""Panel metadata and height caching for virtualized scrolling."""

from __future__ import annotations

from typing import Generic, TypeVar

__all__ = ["Layout"]

T = TypeVar("T")


class Layout(Generic[T]):
    """Pure metadata and height cache for panels.

    Stores panel metadata, caches measured heights (current + last-known),
    and tracks dirty state for incremental offset recomputation.
    """

    def __init__(self) -> None:
        """Initialize layout cache."""
        # panel_id -> measured height at current width
        self._height_cache: dict[int, int] = {}

        # panel_id -> last known height (survives width changes)
        self._last_known_height: dict[int, int] = {}

        # panel_id -> metadata (e.g., is_mounted, panel reference)
        self._metadata: dict[int, dict[str, object]] = {}

    def get_height(self, panel_id: int) -> int | None:
        """Get cached height for panel at current width, or None."""
        return self._height_cache.get(panel_id)

    def get_last_known_height(self, panel_id: int) -> int | None:
        """Get last known height for panel (survives width changes)."""
        return self._last_known_height.get(panel_id)

    def store_height(self, panel_id: int, height: int) -> None:
        """Store measured height for panel."""
        self._height_cache[panel_id] = height
        self._last_known_height[panel_id] = height

    def set_metadata(self, panel_id: int, key: str, value: object) -> None:
        """Store metadata for a panel."""
        if panel_id not in self._metadata:
            self._metadata[panel_id] = {}
        self._metadata[panel_id][key] = value

    def get_metadata(self, panel_id: int, key: str) -> object | None:
        """Retrieve metadata for a panel."""
        return self._metadata.get(panel_id, {}).get(key)

    def discard(self, panel_id: int) -> None:
        """Remove all cached data for a panel (on removal)."""
        self._height_cache.pop(panel_id, None)
        self._last_known_height.pop(panel_id, None)
        self._metadata.pop(panel_id, None)

    def release(self, panel_id: int) -> None:
        """Drop cached height but keep last-known (for off-screen panels)."""
        self._height_cache.pop(panel_id, None)

    def retain_width(self, width: int) -> None:
        """Called after resize to clear width-dependent cache."""
        self._height_cache.clear()

    def clear(self) -> None:
        """Clear all caches."""
        self._height_cache.clear()
        self._last_known_height.clear()
        self._metadata.clear()

    def __len__(self) -> int:
        """Return number of cached panels."""
        return len(self._height_cache)
