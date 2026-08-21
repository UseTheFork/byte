from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class VisibleRange(Generic[T]):
    """The slice of entries the view should draw, plus paint geometry."""

    start: int
    """Index (inclusive) of the first entry to draw, overscan included."""

    stop: int
    """Index (exclusive) after the last entry to draw."""

    entries: list[T]
    """The entries ``[start:stop]``."""

    first_offset: int
    """Virtual y-offset (rows) of ``entries[0]``'s top edge."""

    def __repr__(self) -> str:
        return f"<VisibleRange {self.start}:{self.stop} first_offset={self.first_offset}>"


class Viewport(Generic[T]):
    """Owns scroll position and computes visible range with cumulative offsets.

    The viewport holds an ordered list of entries and, using heights from
    Layout, computes cumulative offsets, total virtual height, and the visible
    range with overscan. Dependency is one-way: Viewport -> Layout.
    """

    def __init__(
        self,
        *,
        estimated_height: int = 1,
        overscan: int = 4,
        spacing: int = 0,
    ) -> None:
        """Initialize viewport with configuration.

        Args:
            estimated_height: Default height for entries not yet measured.
            overscan: Rows to include above/below visible range.
            spacing: Blank rows between consecutive entries.
        """
        self._entries: list[T] = []
        self._width: int = 0
        self._height: int = 0
        self._scroll_y: int = 0

        self._estimated_height = max(1, estimated_height)
        self._overscan = max(0, overscan)
        self._spacing = max(0, spacing)

        # Lazily rebuilt prefix-offset cache: offsets[i] = rows above entry i;
        # offsets[len] = total virtual height.
        self._offsets: list[int] | None = None

        # Incremental rebuild: offsets[0..dirty_from] stay valid; only
        # [dirty_from:] is recomputed.
        self._dirty_from: int = 0

        # Maps entry id -> position for O(1) targeting.
        self._index_of: dict[int, int] = {}

        # Callback to get height for an entry (provided by Layout).
        self._height_fn: Callable[[T], int] | None = None

    def set_height_fn(self, fn: Callable[[T], int]) -> None:
        """Set the function to retrieve height for an entry."""
        self._height_fn = fn

    def set_size(self, width: int, height: int) -> None:
        """Set the viewport's inner size in cells.

        A width change invalidates all offsets (heights are width-dependent).
        """
        if width != self._width:
            self._width = width
            self._invalidate_offsets()
        self._height = height
        self._clamp_scroll()

    def set_entries(self, entries: list[T], entry_id_fn: Callable[[T], int]) -> None:
        """Replace the ordered entry list.

        Args:
            entries: New list of entries.
            entry_id_fn: Function to extract id from an entry.
        """
        self._entries = entries
        self._index_of = {entry_id_fn(entry): i for i, entry in enumerate(entries)}
        self._invalidate_offsets()

    def invalidate_heights(self) -> None:
        """Mark all offsets stale (resize or multiple height changes)."""
        self._invalidate_offsets()

    def invalidate_height_of(self, entry_id: int) -> None:
        """Mark offsets stale from entry onward only (O(1) for last entry)."""
        index = self._index_of.get(entry_id)
        if index is None or self._offsets is None:
            self._invalidate_offsets()
        else:
            self._dirty_from = min(self._dirty_from, index)

    @property
    def total_height(self) -> int:
        """Total virtual height of all entries."""
        return self._prefix()[-1]

    @property
    def max_scroll(self) -> int:
        """Maximum scroll position."""
        return max(0, self.total_height - self._height)

    @property
    def scroll_y(self) -> int:
        """Current scroll position."""
        return self._scroll_y

    def scroll_to_offset(self, y: int) -> None:
        """Set scroll position to y."""
        self._scroll_y = y
        self._clamp_scroll()

    def scroll_to_top(self) -> None:
        """Scroll to top."""
        self._scroll_y = 0

    def scroll_to_bottom(self) -> None:
        """Scroll to bottom."""
        self._scroll_y = self.max_scroll

    def scroll_by(self, delta: int) -> None:
        """Scroll by delta rows."""
        self.scroll_to_offset(self._scroll_y + delta)

    def is_at_bottom(self) -> bool:
        """Check if scrolled to bottom."""
        return self._scroll_y >= self.max_scroll

    def locate(self, y: int) -> tuple[int, int] | None:
        """Map virtual y-offset to (entry_index, local_y).

        Returns None if y is outside content or in a spacer gap.
        """
        prefix = self._prefix()
        n = len(self._entries)

        if n == 0 or y < 0 or y >= prefix[-1]:
            return None

        index = _upper_bound(prefix, y) - 1

        if index < 0 or index >= n:
            return None

        local_y = y - prefix[index]
        if self._height_fn is None:
            return None

        entry_height = self._height_fn(self._entries[index])
        if local_y >= entry_height:
            return None  # in the spacer gap after this entry

        return index, local_y

    def offset_at(self, index: int) -> int:
        """Virtual y-offset of entry at index (O(1) via prefix)."""
        prefix = self._prefix()
        if index < 0 or index >= len(prefix):
            return 0
        return prefix[index]

    def index_of(self, entry_id: int) -> int | None:
        """Position of entry in list, or None (O(1))."""
        return self._index_of.get(entry_id)

    def visible_range(self) -> VisibleRange[T]:
        """Compute entries to draw for current scroll position with overscan."""
        prefix = self._prefix()
        n = len(self._entries)

        if n == 0 or self._height <= 0:
            return VisibleRange(0, 0, [], 0)

        top = max(0, self._scroll_y - self._overscan)
        bottom = self._scroll_y + self._height + self._overscan

        start = _upper_bound(prefix, top) - 1
        start = max(0, min(start, n - 1))

        # advance stop until an entry starts at/after bottom
        stop = start
        while stop < n and prefix[stop] < bottom:
            stop += 1

        return VisibleRange(start, stop, self._entries[start:stop], prefix[start])

    def _prefix(self) -> list[int]:
        """Cumulative offsets: prefix[i] = start row of entry i.

        Rebuilt incrementally from dirty_from.
        """
        n = len(self._entries)
        offsets = self._offsets

        if offsets is None or len(offsets) != n + 1:
            offsets = [0] * (n + 1)
            start = 0
        elif self._dirty_from > n:
            return offsets  # clean
        else:
            start = self._dirty_from

        if self._height_fn is None:
            self._offsets = offsets
            return offsets

        acc = offsets[start] if start > 0 else 0
        last = n - 1

        for i in range(start, n):
            offsets[i] = acc
            acc += self._height_fn(self._entries[i])
            if i < last:
                acc += self._spacing

        offsets[n] = acc
        self._offsets = offsets
        self._dirty_from = n + 1  # clean

        return offsets

    def _invalidate_offsets(self) -> None:
        """Mark all offsets as stale."""
        self._offsets = None
        self._dirty_from = 0

    def _clamp_scroll(self) -> None:
        """Clamp scroll position to valid range."""
        self._scroll_y = max(0, min(self._scroll_y, self.max_scroll))


def _upper_bound(prefix: list[int], value: int) -> int:
    """Index of first element in prefix strictly greater than value (binary search)."""
    lo, hi = 0, len(prefix)
    while lo < hi:
        mid = (lo + hi) // 2
        if prefix[mid] <= value:
            lo = mid + 1
        else:
            hi = mid
    return lo
