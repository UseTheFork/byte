"""Virtualized vertical scroll container for efficient rendering of large chat histories."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.containers import ScrollableContainer
from textual.widget import Widget

if TYPE_CHECKING:
    from byte.tui.widgets.response_panel import ResponsePanel


class HeightPlaceholder(Widget):
    """Lightweight widget that preserves height via min-height CSS. Renders nothing."""

    DEFAULT_CSS = """
    HeightPlaceholder {
        height: auto;
        overflow: hidden;
    }
    """

    def __init__(
        self,
        panel_id: str,
        height: int,
        name: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize placeholder with cached height.

        Args:
            panel_id: The panel ID this placeholder represents.
            height: The cached height in cells.
            name: Optional widget name.
            classes: Optional CSS classes.
            disabled: Whether disabled.
        """
        super().__init__(name=name, id=f"placeholder-{panel_id}", classes=classes, disabled=disabled)
        self.panel_id = panel_id
        self.height = height
        self.styles.min_height = height

    def render(self) -> str:
        """Render nothing."""
        return ""


@dataclass
class PanelSlot:
    """Metadata for a panel in the virtualized container."""

    panel_id: str
    measured_height: int | None = None
    is_mounted: bool = True
    panel: ResponsePanel | None = None
    """ID of the panel."""
    """Cached height after layout (None if not yet measured)."""
    """Whether the real panel is currently mounted in the DOM."""
    """Reference to the ResponsePanel (kept in memory even when not in DOM)."""


class VirtualizedVerticalScroll(ScrollableContainer):
    """Virtualized vertical scroll container that manages panel lifecycle based on viewport.

    Panels are mount/unmounted as the user scrolls, with height-preserving placeholders
    keeping the scroll position intact. The active streaming panel is never virtualized.
    """

    DEFAULT_CSS = """
    VirtualizedVerticalScroll {
        width: 1fr;
        height: 1fr;
        layout: vertical;
        overflow-x: hidden;
        overflow-y: auto;
    }
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        can_focus: bool | None = None,
        can_focus_children: bool | None = None,
        can_maximize: bool | None = None,
    ) -> None:
        """Initialize virtualized scroll container.

        Args:
            *children: Child widgets (typically empty).
            name: Optional widget name.
            id: Optional widget ID.
            classes: Optional CSS classes.
            disabled: Whether disabled.
            can_focus: Whether this container can be focused.
            can_focus_children: Whether children can be focused.
            can_maximize: Whether this can be maximized.
        """
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            can_focus=can_focus,
            can_focus_children=can_focus_children,
            can_maximize=can_maximize,
        )
        self._slots: list[PanelSlot] = []
        self.active_panel_id: str | None = None
        self._reconcile_timer_handle: object | None = None

    async def _cache_panel_height(self, slot: PanelSlot) -> None:
        """Cache the height of a panel.

        Args:
            slot: The slot containing the panel.
        """
        if slot.panel is None or slot.measured_height is not None:
            return

        # Only cache if mounted and sized
        if slot.is_mounted and slot.panel.outer_size.height > 0:
            slot.measured_height = slot.panel.outer_size.height

    async def _mount_panel(self, slot: PanelSlot) -> None:
        """Mount a panel and remove its placeholder if it exists.

        Args:
            slot: The slot containing the panel.
        """
        if slot.panel is None:
            return

        # Remove placeholder if it exists
        try:
            placeholder = self.query_one(f"#placeholder-{slot.panel_id}")
            await placeholder.remove()
        except Exception:
            pass

        # Mount the real panel
        try:
            await self.mount(slot.panel)
            slot.is_mounted = True
            # Cache height after mounting
            await self._cache_panel_height(slot)
            self.refresh(layout=True)
        except Exception:
            pass

    async def add_panel(self, panel: ResponsePanel) -> None:
        """Mount a panel and create a slot for it.

        Args:
            panel: The ResponsePanel to add.
        """
        if panel.id is None:
            raise ValueError("Panel must have an ID")

        panel_id = panel.id

        # Check if slot already exists
        for slot in self._slots:
            if slot.panel_id == panel_id:
                # Already exists, just ensure it's mounted
                if not slot.is_mounted:
                    await self._mount_panel(slot)
                return

        # Create new slot
        slot = PanelSlot(panel_id=panel_id, panel=panel, is_mounted=True)
        self._slots.append(slot)

        # Mount the panel
        await self.mount(panel)
        self.refresh(layout=True)

    def mark_active(self, panel_id: str) -> None:
        """Mark a panel as the active streaming panel (never virtualized).

        Args:
            panel_id: The ID of the panel to mark as active.
        """
        self.active_panel_id = panel_id

    async def _unmount_panel_and_place_holder(self, slot: PanelSlot) -> None:
        """Unmount a panel and replace with a placeholder.

        Args:
            slot: The slot containing the panel.
        """
        if slot.panel is None:
            return

        # Cache height before unmounting
        await self._cache_panel_height(slot)

        # Remove the real panel
        try:
            await slot.panel.remove()
        except Exception:
            pass

        slot.is_mounted = False

        # Mount placeholder with cached height
        if slot.measured_height is not None:
            placeholder = HeightPlaceholder(
                panel_id=slot.panel_id,
                height=slot.measured_height,
            )
            try:
                await self.mount(placeholder)
            except Exception:
                pass

    async def _reconcile(self) -> None:
        """Reconcile mount/unmount state of panels based on viewport visibility.

        Uses a 2x viewport height buffer to pre-load panels before they enter view.
        """
        self._reconcile_timer_handle = None

        if not self._slots:
            return

        # Get viewport bounds
        viewport_top = self.scroll_offset.y
        viewport_height = self.size.height
        viewport_bottom = viewport_top + viewport_height
        buffer = viewport_height * 2

        # Compute cumulative Y offsets for each panel
        cumulative_y = 0
        panel_positions: list[tuple[PanelSlot, int, int]] = []  # (slot, top, bottom)

        for slot in self._slots:
            top = cumulative_y
            # Use cached height if available, else use 1 (will update after mounting)
            height = slot.measured_height if slot.measured_height is not None else 1
            bottom = top + height
            panel_positions.append((slot, top, bottom))
            cumulative_y = bottom

        # Reconcile each panel
        for slot, panel_top, panel_bottom in panel_positions:
            should_mount = (
                # Within viewport with buffer
                (panel_top < viewport_bottom + buffer and panel_bottom > viewport_top - buffer)
                # Never virtualize panels without measured height (not yet laid out)
                or slot.measured_height is None
                # Never virtualize the active panel
                or slot.panel_id == self.active_panel_id
            )

            if should_mount and not slot.is_mounted and slot.panel is not None:
                # Mount the real panel
                await self._mount_panel(slot)
            elif not should_mount and slot.is_mounted and slot.panel is not None:
                # Unmount and replace with placeholder
                await self._unmount_panel_and_place_holder(slot)

    def _schedule_reconcile(self) -> None:
        """Schedule reconciliation with debouncing (0.2s)."""
        if self._reconcile_timer_handle is not None:
            self._reconcile_timer_handle.stop()

        self._reconcile_timer_handle = self.set_timer(0.2, self._reconcile)

    def clear_active(self) -> None:
        """Clear the active panel marker."""
        self.active_panel_id = None
        # Trigger reconciliation to potentially virtualize the panel
        self._schedule_reconcile()

    def get_panel(self, panel_id: str) -> ResponsePanel | None:
        """Get a panel by ID (mounted or cached).

        Args:
            panel_id: The ID to look up.

        Returns:
            The ResponsePanel if found, else None.
        """
        for slot in self._slots:
            if slot.panel_id == panel_id and slot.panel is not None:
                return slot.panel
        return None

    async def remove_panel(self, panel_id: str) -> None:
        """Remove a panel and its slot.

        Args:
            panel_id: The ID of the panel to remove.
        """
        slot_index = None
        for i, slot in enumerate(self._slots):
            if slot.panel_id == panel_id:
                slot_index = i
                break

        if slot_index is not None:
            slot = self._slots.pop(slot_index)
            if slot.panel is not None and slot.is_mounted:
                try:
                    await slot.panel.remove()
                except Exception:
                    pass
            # Try to remove placeholder
            try:
                placeholder = self.query_one(f"#placeholder-{panel_id}")
                await placeholder.remove()
            except Exception:
                pass

    async def remove_all_panels(self) -> None:
        """Remove all panels and slots."""
        # Make a copy of slots list since we'll be modifying it
        slots_copy = self._slots.copy()
        for slot in slots_copy:
            await self.remove_panel(slot.panel_id)

    async def ensure_panel_visible(self, panel_id: str) -> None:
        """Restore a panel from placeholder (if needed) and scroll to it.

        Args:
            panel_id: The ID of the panel to make visible.
        """
        # Find the slot
        slot = None
        for s in self._slots:
            if s.panel_id == panel_id:
                slot = s
                break

        if slot is None or slot.panel is None:
            return

        # If it's currently a placeholder, restore it
        if not slot.is_mounted:
            await self._mount_panel(slot)

        # Scroll to the panel
        try:
            slot.panel.scroll_visible(animate=True)
        except Exception:
            pass

    def watch_scroll_y(self, _old_value: float, _new_value: float) -> None:
        """Debounce scroll events and trigger reconciliation.

        Args:
            _old_value: Previous scroll Y position.
            _new_value: New scroll Y position.
        """
        self._schedule_reconcile()
