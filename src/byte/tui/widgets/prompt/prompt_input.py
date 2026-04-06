from typing import TYPE_CHECKING, Callable

from textual import containers, getters, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.content import Content
from textual.message import Message
from textual.reactive import var
from textual.widgets import Label, TextArea

from byte.tui import Messages

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class PromptTextArea(TextArea):
    class Submitted(Message):
        def __init__(self, markdown: str) -> None:
            self.markdown = markdown
            super().__init__()

    BINDING_GROUP_TITLE = "Prompt"

    BINDINGS = [
        Binding(
            "enter",
            "submit",
            "Send",
            key_display="⏎",
            priority=True,
            tooltip="Send the prompt to the agent",
        ),
        Binding(
            "ctrl+j,shift+enter",
            "newline",
            "Line",
            key_display="⇧+⏎",
            tooltip="Insert a new line character",
        ),
        Binding(
            "ctrl+j,shift+enter",
            "multiline_submit",
            "Send",
            key_display="⇧+⏎",
            tooltip="Send the prompt to the agent",
        ),
        Binding(
            "tab",
            "tab_complete",
            "Complete",
            tooltip="Complete path (if possible)",
            priority=True,
            show=False,
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
        complete_callback: Callable[[str], list[str]] | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._autocomplete = None

    def on_mount(self) -> None:
        self.highlight_cursor_line = False
        self.hide_suggestion_on_blur = False

    async def _on_key(self, event) -> None:
        if self._autocomplete and self._autocomplete.handle_key(event.key):
            event.prevent_default()
            event.stop()
            return

        await super()._on_key(event)

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
        self.post_message(Messages.UserInputSubmitted(self.text))
        self.clear()

    def action_newline(self) -> None:
        self.insert("\n")


class PromptInput(containers.VerticalGroup):
    PROMPT_NULL = " "
    PROMPT_AI = Content.styled("❯", "$text-secondary")  # noqa: RUF001
    PROMPT_MULTILINE = Content.styled("☰", "$text-secondary")

    multi_line = var(False)

    prompt_label = getters.query_one("#prompt", Label)
    prompt_text_area = getters.query_one(PromptTextArea)

    @on(TextArea.Changed)
    async def on_text_area_changed(self, event: TextArea.Changed) -> None:
        text = event.text_area.text

        self.multi_line = "\n" in text or "```" in text

        self.update_prompt()

    def update_prompt(self):
        """Update the prompt according to the current mode."""
        self.prompt_label.update(
            self.PROMPT_MULTILINE if self.multi_line else self.PROMPT_AI,
            layout=False,
        )

        # prompt_message = self.app.settings.get("ui.prompt_message", str)
        prompt_message = " "
        self.prompt_text_area.placeholder = Content.assemble(
            f"{prompt_message}\t".expandtabs(8),
            ("▌/▐", "r"),
            " commands ",
            ("▌@▐", "r"),
            " files",
        )

    def compose(self) -> ComposeResult:
        with containers.HorizontalGroup(id="text-prompt"):
            yield Label(self.PROMPT_AI, id="prompt", markup=False)
            yield PromptTextArea(id="input").data_bind(multi_line=PromptInput.multi_line)
