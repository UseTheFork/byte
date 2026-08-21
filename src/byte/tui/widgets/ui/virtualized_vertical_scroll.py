from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.containers import ScrollableContainer
from textual.timer import Timer
from textual.widget import Widget

from byte.tui.widgets.ui.layout import Layout
from byte.tui.widgets.ui.viewport import Viewport

if TYPE_CHECKING:
    from byte.tui.widgets.response_panel import ResponsePanel


class HeightPlaceholder(Widget):
    """Preserve height via min-height CSS."""

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
        """Initialize placeholder with cached height."""
        super().__init__(name=name, id=f"placeholder-{panel_id}", classes=classes, disabled=disabled)
        self.panel_id = panel_id
        self.height = height
        self.styles.min_height = height

    def render(self) -> str:
        """Return empty string."""
        return ""


@dataclass
class PanelSlot:
    """Store metadata for a panel in the virtualized container."""

    panel_id: str
    measured_height: int | None = None
    is_mounted: bool = True
    panel: ResponsePanel | None = None


class VirtualizedVerticalScroll(ScrollableContainer):
    """Manage virtualized panel lifecycle based on viewport visibility.

    Uses Viewport for scroll state and visible range computation, and Layout
    for panel metadata and height caching. Reconciliation logic determines
    which panels should be mounted vs. replaced with placeholders.
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

    def _get_slot_height(self, slot: PanelSlot) -> int:
        """Get height for a slot from layout cache or estimate."""
        panel_id_int = hash(slot.panel_id) & 0x7FFFFFFF
        cached = self._layout.get_height(panel_id_int)
        if cached is not None:
            return cached
        last_known = self._layout.get_last_known_height(panel_id_int)
        if last_known is not None:
            return last_known
        return self._viewport._estimated_height

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
        """Initialize virtualized scroll container."""
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
        self._reconcile_timer_handle: Timer | None = None

        # Initialize viewport and layout
        self._viewport: Viewport[PanelSlot] = Viewport(estimated_height=1, overscan=4, spacing=0)
        self._layout: Layout[str] = Layout()

        # Set height function for viewport
        self._viewport.set_height_fn(self._get_slot_height)

    async def _cache_panel_height(self, slot: PanelSlot) -> None:
        """Cache the height of a panel."""
        if slot.panel is None or slot.measured_height is not None:
            return

        # Only cache if mounted and sized
        if slot.is_mounted and slot.panel.outer_size.height > 0:
            slot.measured_height = slot.panel.outer_size.height
            panel_id_int = hash(slot.panel_id) & 0x7FFFFFFF
            self._layout.store_height(panel_id_int, slot.measured_height)

    async def _mount_panel(self, slot: PanelSlot) -> None:
        """Mount a panel and remove its placeholder if it exists."""
        if slot.panel is None:
            return

        # Remove placeholder if it exists
        try:
            placeholder = self.query_one(f"#placeholder-{slot.panel_id}")
            await placeholder.remove()
        except (Exception,):
            pass

        # Mount the real panel
        try:
            await self.mount(slot.panel)
            slot.is_mounted = True
            # Cache height after mounting
            await self._cache_panel_height(slot)
            self.refresh(layout=True)
        except (Exception,):
            pass

    async def add_panel(self, panel: ResponsePanel) -> None:
        """Mount a panel and create a slot for it."""
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

        # Update viewport with new entries
        self._viewport.set_entries(self._slots, lambda s: hash(s.panel_id) & 0x7FFFFFFF)

        # Mount the panel
        await self.mount(panel)
        self.refresh(layout=True)

    def mark_active(self, panel_id: str) -> None:
        """Mark a panel as the active streaming panel (never virtualized)."""
        self.active_panel_id = panel_id

    async def _unmount_panel_and_place_holder(self, slot: PanelSlot) -> None:
        """Unmount a panel and replace with a placeholder."""
        if slot.panel is None:
            return

        # Cache height before unmounting
        await self._cache_panel_height(slot)

        # Remove the real panel
        try:
            await slot.panel.remove()
        except (Exception,):
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
            except (Exception,):
                pass

    async def _reconcile(self) -> None:
        """Reconcile mount/unmount state of panels based on viewport visibility."""
        self._reconcile_timer_handle = None

        if not self._slots:
            return

        # Update viewport size
        self._viewport.set_size(self.size.width, self.size.height)

        # Update scroll position
        self._viewport.scroll_to_offset(int(self.scroll_offset.y))

        # Get visible range
        visible_range = self._viewport.visible_range()

        # Reconcile each panel
        for i, slot in enumerate(self._slots):
            should_mount = (
                # Within visible range (with overscan)
                (i >= visible_range.start and i < visible_range.stop)
                # Never virtualize panels without measured height (not yet laid out)
                or slot.measured_height is None
                # Never virtualize the active panel
                or slot.panel_id == self.active_panel_id
            )

            if should_mount and not slot.is_mounted and slot.panel is not None:
                await self._mount_panel(slot)
            elif not should_mount and slot.is_mounted and slot.panel is not None:
                await self._unmount_panel_and_place_holder(slot)

    def _schedule_reconcile(self) -> None:
        """Schedule reconciliation with debouncing."""
        if self._reconcile_timer_handle is not None:
            self._reconcile_timer_handle.stop()

        self._reconcile_timer_handle = self.set_timer(0.2, self._reconcile)

    def clear_active(self) -> None:
        """Clear the active panel marker."""
        self.active_panel_id = None
        self._schedule_reconcile()

    def get_panel(self, panel_id: str) -> ResponsePanel | None:
        """Get a panel by ID (mounted or cached)."""
        for slot in self._slots:
            if slot.panel_id == panel_id and slot.panel is not None:
                return slot.panel
        return None

    async def remove_panel(self, panel_id: str) -> None:
        """Remove a panel and its slot."""
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
                except (Exception,):
                    pass
            # Try to remove placeholder
            try:
                placeholder = self.query_one(f"#placeholder-{panel_id}")
                await placeholder.remove()
            except (Exception,):
                pass

            # Update viewport
            self._viewport.set_entries(self._slots, lambda s: hash(s.panel_id) & 0x7FFFFFFF)

            # Clean up layout cache
            panel_id_int = hash(panel_id) & 0x7FFFFFFF
            self._layout.discard(panel_id_int)

    async def remove_all_panels(self) -> None:
        """Remove all panels and slots."""
        slots_copy = self._slots.copy()
        for slot in slots_copy:
            await self.remove_panel(slot.panel_id)

    async def ensure_panel_visible(self, panel_id: str) -> None:
        """Restore a panel from placeholder (if needed) and scroll to it."""
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
        except (Exception,):
            pass

    def watch_scroll_y(self, old_value: float, new_value: float) -> None:
        """Debounce scroll events and trigger reconciliation."""
        super().watch_scroll_y(old_value, new_value)
        self._schedule_reconcile()
