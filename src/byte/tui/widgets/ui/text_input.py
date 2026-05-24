import asyncio
from typing import TYPE_CHECKING

from textual import getters
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalGroup
from textual.content import Content
from textual.message import Message
from textual.reactive import var
from textual.widgets import Markdown, Rule, TextArea
from typing_extensions import Self

from byte.tui import Messages
from byte.tui.schemas import Answer, AnswerCancelled, Ask

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class TextInputTextArea(TextArea):
    class Submitted(Message):
        def __init__(self, markdown: str) -> None:
            self.markdown = markdown
            super().__init__()

    BINDINGS = [
        Binding(
            "enter",
            "submit",
            "Send",
            # key_display="\u23ce ",
            priority=True,
            tooltip="Send the prompt to the agent",
        ),
        Binding(
            "ctrl+j,shift+enter",
            "newline",
            "Line",
            # key_display="\u21e7 + \u23ce ",
            tooltip="Insert a new line character",
        ),
    ]

    app: ByteTUI

    multi_line = var(False, bindings=True)

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        compact: bool = True,
        placeholder: str | Content = "",
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled, compact=compact, placeholder=placeholder)
        self._autocomplete = None

    def on_mount(self) -> None:
        self.highlight_cursor_line = False
        self.hide_suggestion_on_blur = False

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "newline" and self.multi_line:
            return False
        if action == "submit" and self.multi_line:
            return False
        if action == "multiline_submit":
            return self.multi_line
        return True

    def action_multiline_submit(self) -> None:
        self.post_message(Messages.UserInputSubmitted(self.text))
        self.clear()

    def action_submit(self) -> None:
        self.post_message(TextInputTextArea.Submitted(self.text))
        self.clear()

    def action_newline(self) -> None:
        self.insert("\n")


class TextInput(VerticalGroup):
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
        TextInput {
            background: transparent;
            height: auto;
            
            & VerticalGroup {
                background: transparent;
            }
            
            & Markdown {
                height: auto;
            }
            
            & TextArea {
                background: transparent;
                border: none;
                padding: 0 1;
                height: auto;
                
                &:focus {
                    border: none;
                }
            }
        }
        """

    app: ByteTUI

    _result_future: asyncio.Future[Answer | list[Answer] | str | AnswerCancelled]
    submitted: var[bool] = var(False)

    text_input = getters.query_one(TextInputTextArea)

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

    def action_exit_now(self):
        if not self.submitted:
            self.submit_value(AnswerCancelled())

    def on_text_input_text_area_submitted(self, event: TextInputTextArea.Submitted) -> None:
        """Handle when user presses Enter in the input field."""
        if not self.submitted:
            value = event.markdown.strip()
            self.submit_value(value)

    def focus(self, scroll_visible: bool = True) -> Self:
        if self.text_input:
            self.text_input.focus(scroll_visible)
            return self
        else:
            return super().focus(scroll_visible)

    def compose(self) -> ComposeResult:
        if self.ask:
            yield Markdown(self.ask.question)
        yield Rule()
        self.text_input = TextInputTextArea(  # ty:ignore[invalid-assignment]
            placeholder="Type your answer...",
            id="text-input-area",
        )
        yield self.text_input

    def submit_value(self, value: str | AnswerCancelled):
        """Submit the current value and disable the input."""
        self.submitted = True

        # For text input, we return the string directly in the future
        # but post an Answer message for consistency
        if isinstance(value, str):
            answer = Answer(label=value, value=value)
        else:
            answer = value

        # Resolve the future if present
        if self._result_future and not self._result_future.done():
            loop = self._result_future.get_loop()
            loop.call_soon_threadsafe(self._result_future.set_result, answer)

        self.disabled = True
        self.remove_class("border-round")

        if isinstance(answer, AnswerCancelled):
            self.add_class("border-round-error")
        else:
            self.add_class("border-round-dim")

        # Post message with the string value wrapped in Answer if not cancelled
        self.post_message(Messages.Answer(answer))
