from __future__ import annotations

import asyncio

from textual import getters
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalGroup
from textual.reactive import var
from textual.widgets import Input as TextualInput
from typing_extensions import Self

from byte.tui import Messages
from byte.tui.schemas import Answer, AnswerCancelled, Ask


class Input(VerticalGroup):
    """An input widget that allows text input from the user."""

    BINDINGS = [
        Binding(
            "escape",
            "exit_now",
            description="cancel input",
            priority=True,
        ),
    ]

    DEFAULT_CSS = """
        Input {
            background: transparent;
            height: auto;
            
            & VerticalGroup {
                background: transparent;
            }
            
            & TextualInput {
                background: transparent;
                border: none;
                padding: 0 1;
                
                &:focus {
                    border: none;
                }
            }
        }
        """

    _result_future: asyncio.Future[Answer | list[Answer] | str | AnswerCancelled]
    submitted: var[bool] = var(False)

    text_input = getters.query_one(TextualInput)

    ask: var[Ask | None] = var(None)

    def __init__(
        self,
        ask: Ask,
        name: str | None = None,
        default: str = "",
        mandatory: bool = True,
        *,
        id: str | None = None,
        classes: str | None = "border-round",
        disabled: bool = False,
    ):
        """
        Args:
            ask: The Ask object containing question and result future.
            default: The default text value.
            mandatory: Whether a response is mandatory.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.ask = ask

        # Extract these immediately for use in compose()
        self._result_future = ask.result_future

        self.default = default
        self.mandatory = mandatory

    def on_mount(self):
        self.border_title = self.ask.question  # ty:ignore[possibly-missing-attribute]
        self.styles.height = 3

    def action_exit_now(self):
        if not self.submitted:
            self.submit_value(AnswerCancelled())

    def on_input_submitted(self, event: TextualInput.Submitted) -> None:
        """Handle when user presses Enter in the input field."""
        if not self.submitted:
            value = event.value.strip()
            self.submit_value(value)

    def focus(self, scroll_visible: bool = True) -> Self:
        if self.text_input:
            self.text_input.focus(scroll_visible)
            return self
        else:
            return super().focus(scroll_visible)

    def compose(self) -> ComposeResult:
        self.text_input = TextualInput(
            value=self.default,
            placeholder="Type your answer...",
        )
        yield self.text_input

    def submit_value(self, value: str | AnswerCancelled):
        """Submit the current value and disable the input."""
        self.submitted = True

        # Resolve the future if present
        if self._result_future and not self._result_future.done():
            self._result_future.set_result(value)

        self.disabled = True
        self.remove_class("border-round")

        if isinstance(value, AnswerCancelled):
            self.add_class("border-round-error")
        else:
            self.add_class("border-round-dim")

        # Post message with the string value wrapped in Answer if not cancelled
        if isinstance(value, AnswerCancelled):
            self.post_message(Messages.Answer(value))
        else:
            # For text input, we return the string directly in the future
            # but post an Answer message for consistency
            answer = Answer(label=value, value=value)
            self.post_message(Messages.Answer(answer))
