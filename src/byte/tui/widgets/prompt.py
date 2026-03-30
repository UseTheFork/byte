from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Self

from textual import containers, events, getters, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.content import Content
from textual.message import Message
from textual.reactive import var
from textual.widget import Widget
from textual.widgets import Label, TextArea
from textual.widgets.text_area import Selection

from byte.tui import Messages
from byte.tui.widgets.flash import Flash
from byte.tui.widgets.highlighted_textarea import HighlightedTextArea
from byte.tui.widgets.question import Ask, Question
from byte.tui.widgets.text_area_auto_complete import TextAreaAutoComplete

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class AgentInfo(Label):
    pass


class ModeInfo(Label):
    pass


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

    project_path = var(Path())

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
        # if event.key != "escape":
        #     self.suggestions = None
        #     self.suggestion = ""

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


class PromptContainer(containers.HorizontalGroup):
    def on_mouse_down(self, event: events.MouseUp) -> None:
        for child in self.query("*"):
            if child.has_focus:
                return
        prompt_text_area = self.query_one(PromptTextArea)
        if not prompt_text_area.has_focus:
            prompt_text_area.focus()


class StatusLine(Label):
    status: var[str] = var("")

    def watch_status(self, status: str) -> None:
        self.set_class(not bool(status), "-hidden")
        self.update(status)
        self.tooltip = status


class Prompt(containers.VerticalGroup):
    @dataclass
    class CursorEscapingTop(Message):
        pass

    @dataclass
    class CursorEscapingBottom(Message):
        pass

    BINDINGS = [
        Binding("escape", "dismiss", "Dismiss", show=False),
    ]

    PROMPT_NULL = " "
    PROMPT_AI = Content.styled("❯", "$text-secondary")  # noqa: RUF001
    PROMPT_MULTILINE = Content.styled("☰", "$text-secondary")

    prompt_container = getters.query_one("#prompt-container", Widget)
    prompt_text_area = getters.query_one(PromptTextArea)
    prompt_label = getters.query_one("#prompt", Label)
    question = getters.query_one(Question)

    # current_directory = getters.query_one(CondensedPath)
    # path_search = getters.query_one(PathSearch)
    # question = getters.query_one(Question)
    # mode_switcher = getters.query_one(ModeSwitcher)

    multi_line = var(False)

    project_path = var(Path, init=False)
    working_directory = var("")
    agent_info = var(Content(""))
    _ask: var[Ask | None] = var(None)

    status: var[str] = var("")

    app: ByteTUI

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
        self.ask_queue: list[Ask] = []
        self.complete_callback = complete_callback

    @property
    def text(self) -> str:
        return self.prompt_text_area.text

    @text.setter
    def text(self, text: str) -> None:
        self.prompt_text_area.text = text
        self.prompt_text_area.selection = Selection.cursor(self.prompt_text_area.get_cursor_line_end_location())

    def ask(self, ask: Ask) -> None:
        """Replace the textarea prompt with a menu of options.

        Args:
            ask: An `Ask` instance which contains a question and responses.
        """
        self.ask_queue.append(ask)
        # TODO: What does this do?
        # self.app.terminal_alert()
        if self._ask is None:
            self._ask = self.ask_queue.pop(0)

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

    def focus(self, scroll_visible: bool = True) -> Self:
        if self._ask is not None:
            self.question.focus()
        else:
            self.query(HighlightedTextArea).focus()
        return self

    def append(self, text: str) -> None:
        self.query_one(HighlightedTextArea).insert(text, maintain_selection_offset=False)

    @on(TextArea.Changed)
    async def on_text_area_changed(self, event: TextArea.Changed) -> None:
        text = event.text_area.text

        self.multi_line = "\n" in text or "```" in text

        self.update_prompt()

    @on(Messages.PromptSuggestion)
    def on_prompt_suggestion(self, event: Messages.PromptSuggestion) -> None:
        event.stop()
        self.prompt_text_area.suggestion = event.suggestion

    @on(Question.Answer)
    def on_question_answer(self, event: Question.Answer) -> None:
        """Question has been answered."""
        event.stop()

        def remove_question() -> None:
            """Remove the question and restore the text prompt."""
            if self.ask_queue:
                self._ask = self.ask_queue.pop(0)
            else:
                self._ask = None
                # TODO: This
            # self.app.terminal_alert(False)

        if self._ask is not None and (callback := self._ask.callback) is not None:
            callback(event.answer)

        self.set_timer(0.3, remove_question)

    def compose(self) -> ComposeResult:
        # yield PathSearch(self.project_path).data_bind(root=Prompt.project_path)
        yield Flash()
        yield TextAreaAutoComplete("#input")
        with PromptContainer(id="prompt-container"):
            yield Question()
            with containers.HorizontalGroup(id="text-prompt"):
                yield Label(self.PROMPT_AI, id="prompt", markup=False)
                yield PromptTextArea(id="input").data_bind(
                    multi_line=Prompt.multi_line,
                    project_path=Prompt.project_path,
                )
        with containers.HorizontalGroup(id="info-container"):
            yield AgentInfo()
            # yield CondensedPath().data_bind(path=Prompt.working_directory)
            yield StatusLine(markup=False).data_bind(status=Prompt.status)
            # yield ModeSwitcher()
            yield ModeInfo("mode")

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        return True

    def action_dismiss(self) -> None:
        pass
