from __future__ import annotations

import asyncio

from rich.text import Text
from textual import getters
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalGroup
from textual.reactive import var
from textual.widgets import Label, ListItem, ListView
from typing_extensions import Self

from byte.tui import Messages
from byte.tui.constants import SQUARE_FILLED, SQUARE_OUTLINE
from byte.tui.schemas import Answer, AnswerCancelled, Ask


# Credits to https://github.com/robvanderleek/inquirer-textual/blob/main/inquirer_textual/widgets/InquirerSelect.py
class ChoiceLabel(Label):
    DEFAULT_CSS = """
        ChoiceLabel {
            background: transparent;
        }
        """
    item: var

    def _get_text(self, item: Answer, highlight_indices: list[int] | None = None) -> Text:
        result = Text(str(item.label))
        return result

    def __init__(self, item: Answer, highlight_indices: list[int] | None = None):
        self._text = self._get_text(item, highlight_indices)
        super().__init__(Text(f"{SQUARE_OUTLINE} ").append_text(self._text))
        self.item = item

    def add_pointer(self):
        self.update(Text(f"{SQUARE_FILLED} ").append_text(self._text))

    def remove_pointer(self):
        self.update(Text(f"{SQUARE_OUTLINE} ").append_text(self._text))


class Select(VerticalGroup):
    """A select widget that allows a single selection from a list of choices."""

    BINDINGS = [
        Binding(
            "escape",
            "exit_now",
            description="cancel selection",
            priority=True,
        ),
    ]

    DEFAULT_CSS = """
        Select {
            background: transparent;
            & VerticalGroup {
                background: transparent;
            }
            & ListView {
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
    selected_item: var[Answer | AnswerCancelled] = var(AnswerCancelled())

    list_view = getters.query_one(ListView)

    ask: var[Ask | None] = var(None)

    def __init__(
        self,
        ask: Ask,
        name: str | None = None,
        default: Answer | None = None,
        mandatory: bool = True,
        *,
        id: str | None = None,
        classes: str | None = "border-round",
        disabled: bool = False,
    ):
        """
        Args:
            default (str | Choice | None): The default choice to pre-select.
            mandatory (bool): Whether a response is mandatory.
            height (int | str | None): If None, for inline apps the height will be determined based on the number of choices.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.ask = ask

        # Extract these immediately for use in compose()
        self.options = ask.options
        self._result_future = ask.result_future

        self.selected_label: ChoiceLabel | None = None

        self.default = default
        self.selected_value: str | Answer | None = None
        self.show_result: bool = False

        self.mandatory = mandatory

    def on_mount(self):
        self.border_title = self.ask.question
        self.styles.height = len(self.options) + 2

    def action_exit_now(self):
        if self.selected_label:
            self.selected_label.remove_pointer()

        self.submit_current_value(AnswerCancelled())

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if self.selected_label:
            self.selected_label.remove_pointer()
        label = event.item.query_one(ChoiceLabel)  # ty:ignore[unresolved-attribute]
        label.add_pointer()
        self.selected_label = label
        self.selected_item = label.item

    def on_list_view_selected(self, _: ListView.Selected):
        self.submit_current_value(self.selected_item)

    def focus(self, scroll_visible: bool = True) -> Self:
        if self.list_view:
            self.list_view.focus(scroll_visible)
            return self
        else:
            return super().focus(scroll_visible)

    def current_value(self):
        return self.selected_item

    def compose(self) -> ComposeResult:
        initial_index = 0
        items: list[ListItem] = []
        for idx, option in enumerate(self.options):  # ty:ignore[invalid-argument-type]
            list_item = ListItem(ChoiceLabel(option))  # ty:ignore[invalid-argument-type]
            items.append(list_item)
            if self.default and option == self.default:
                initial_index = idx
        self.list_view = ListView(*items, initial_index=initial_index)  # ty:ignore[invalid-assignment]
        yield self.list_view

    def submit_current_value(self, answer: Answer | AnswerCancelled):
        # Resolve the future if present in the other loop since this is usually done via a worker.
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
