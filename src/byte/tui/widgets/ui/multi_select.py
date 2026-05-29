import asyncio

from rich.text import Text
from textual import getters
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalGroup
from textual.reactive import var
from textual.widgets import Label, ListItem, ListView, Markdown, Rule
from typing_extensions import Self

from byte.tui import Messages
from byte.tui.constants import SQUARE_FILLED, SQUARE_OUTLINE
from byte.tui.schemas import Answer, AnswerCancelled, Ask


class ChoiceLabel(Label):
    """Label for multi-select choices with checkbox indicator."""

    DEFAULT_CSS = """
        ChoiceLabel {
            background: transparent;
        }
        """

    def _get_text(self, item: Answer) -> Text:
        result = Text(str(item.label))
        return result

    def __init__(self, item: Answer, selected: bool = False):
        self._text = self._get_text(item)
        checkbox = "[\u2717]" if selected else "[ ]"  # [×] or [ ]
        super().__init__(Text(f"{SQUARE_OUTLINE} ").append_text(self._text).append_text(f" {checkbox}"))
        self.item = item
        self.selected = selected

    def add_pointer(self) -> None:
        """Show pointer (highlight) for currently focused item."""
        checkbox = "[\u2717]" if self.selected else "[ ]"
        self.update(Text(f"{SQUARE_FILLED} ").append_text(self._text).append_text(f" {checkbox}"))

    def remove_pointer(self) -> None:
        """Hide pointer for unfocused item."""
        checkbox = "[\u2717]" if self.selected else "[ ]"
        self.update(Text(f"{SQUARE_OUTLINE} ").append_text(self._text).append_text(f" {checkbox}"))

    def toggle_selection(self) -> None:
        """Toggle selection state and update visual."""
        self.selected = not self.selected
        checkbox = "[\u2717]" if self.selected else "[ ]"
        self.update(Text(f"{SQUARE_FILLED} ").append_text(self._text).append_text(f" {checkbox}"))


class MultiSelect(VerticalGroup):
    """A multi-select widget that allows selection of multiple items from a list."""

    BINDINGS = [
        Binding(
            "escape",
            "exit_now",
            description="cancel selection",
            priority=True,
        ),
        Binding(
            "enter",
            "submit_selection",
            description="confirm selection",
            priority=True,
        ),
    ]

    DEFAULT_CSS = """
        MultiSelect {
            height: auto;
            background: transparent;
            & VerticalGroup {
                background: transparent;
            }
            & Markdown {
                height: auto;
            }
            & ListView {
                height: auto;
                background: transparent;
                & > ListItem {
                    color: $foreground;
                    height: auto;
                    overflow: hidden hidden;
                    width: 1fr;

                    &.-hovered {
                        background: transparent;
                    }
                    
                    &.-highlight {
                        color: $primary;
                        background: transparent;
                    }
                }

                &:focus {
                    & > ListItem.-highlight {
                        color: $primary;
                        background: transparent;
                    }
                }
            }
        }
        """

    _result_future: asyncio.Future[Answer | list[Answer] | str | AnswerCancelled]
    selected_indices: set[int]

    list_view = getters.query_one(ListView)

    ask: var[Ask | None] = var(None)

    def __init__(
        self,
        ask: Ask,
        name: str | None = None,
        *,
        id: str | None = None,
        classes: str | None = "border-round",
        disabled: bool = False,
    ) -> None:
        """Initialize MultiSelect widget.

        Args:
            ask: Ask schema containing question, options, and result_future
            name: Optional widget name
            id: Optional widget id
            classes: Optional CSS classes
            disabled: Whether widget is initially disabled
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.ask = ask
        self.options = ask.options
        self._result_future = ask.result_future
        self.selected_indices: set[int] = set()
        self.selected_label: ChoiceLabel | None = None

    def action_exit_now(self) -> None:
        """Cancel selection and resolve with AnswerCancelled."""
        if self.selected_label:
            self.selected_label.remove_pointer()
        self.submit_current_value(AnswerCancelled())

    def action_submit_selection(self) -> None:
        """Submit the current selection (enter key)."""
        selected_answers = self._get_selected_answers()
        self.submit_current_value(selected_answers)

    def _get_selected_answers(self) -> list[Answer]:
        """Get list of Answer objects for all selected indices."""
        selected: list[Answer] = []
        if self.options:
            for idx in sorted(self.selected_indices):
                if idx < len(self.options):
                    selected.append(self.options[idx])
        return selected

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Handle ListView highlight (cursor movement)."""
        if self.selected_label:
            self.selected_label.remove_pointer()
        label = event.item.query_one(ChoiceLabel)  # type: ignore[union-attr]
        label.add_pointer()
        self.selected_label = label

    def on_list_view_selected(self, _: ListView.Selected) -> None:
        """Handle ListView selected event (space or default select key).

        Override to toggle selection instead of submitting.
        """
        if self.selected_label:
            idx = self._get_current_index()
            if idx is not None:
                if idx in self.selected_indices:
                    self.selected_indices.remove(idx)
                else:
                    self.selected_indices.add(idx)
                self.selected_label.toggle_selection()

    def _get_current_index(self) -> int | None:
        """Get the index of the currently highlighted item."""
        if self.list_view and self.selected_label:
            items = self.list_view.children
            for idx, item in enumerate(items):
                if isinstance(item, ListItem):
                    try:
                        label = item.query_one(ChoiceLabel)
                        if label == self.selected_label:
                            return idx
                    except Exception:
                        pass
        return None

    def focus(self, scroll_visible: bool = True) -> Self:
        """Focus the ListView."""
        if self.list_view:
            self.list_view.focus(scroll_visible)
            return self
        else:
            return super().focus(scroll_visible)

    def compose(self) -> ComposeResult:
        """Compose the widget structure."""
        if self.ask:
            yield Markdown(self.ask.question)
        yield Rule()

        items: list[ListItem] = []
        if self.options:
            for option in self.options:
                list_item = ListItem(ChoiceLabel(option, selected=False))
                items.append(list_item)

        self.list_view = ListView(*items)  # type: ignore[assignment]
        yield self.list_view

    def submit_current_value(self, answer: list[Answer] | AnswerCancelled) -> None:
        """Submit the selection and resolve the future.

        Args:
            answer: Either a list of Answer objects or AnswerCancelled
        """
        if self._result_future and not self._result_future.done():
            loop = self._result_future.get_loop()
            loop.call_soon_threadsafe(self._result_future.set_result, answer)

        self.disabled = True
        self.remove_class("border-round")

        if isinstance(answer, AnswerCancelled):
            self.add_class("border-round-error")
        else:
            self.add_class("border-round-dim")

        self.post_message(Messages.Answer(answer))
