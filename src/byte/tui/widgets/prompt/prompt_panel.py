from typing import TYPE_CHECKING

from textual import containers, getters
from textual.app import ComposeResult
from textual.content import Content
from textual.reactive import reactive, var
from textual.widgets.text_area import Selection

from byte.tui.widgets.prompt.analytics import Analytics
from byte.tui.widgets.prompt.flash import Flash
from byte.tui.widgets.prompt.prompt_input import PromptInput, PromptTextArea
from byte.tui.widgets.ui.text_area_auto_complete import TextAreaAutoComplete

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class PromptContainer(containers.HorizontalGroup):
    pass
    # def on_mouse_down(self, event: events.MouseUp) -> None:
    #     for child in self.query("*"):
    #         if child.has_focus:
    #             return
    #     prompt_text_area = self.query_one(PromptTextArea)
    #     if not prompt_text_area.has_focus:
    #         prompt_text_area.focus()


class PromptPanel(containers.VerticalGroup):
    prompt_container = getters.query_one("#prompt-container", PromptContainer)
    prompt_text_area = getters.query_one(PromptTextArea)

    prompt_input = getters.query_one(PromptInput)

    working_directory = var("")
    agent_info = var(Content(""))

    status: var[str] = var("")
    allow_input_submit = reactive(True)

    app: ByteTUI

    @property
    def text(self) -> str:
        return self.prompt_text_area.text

    @text.setter
    def text(self, text: str) -> None:
        self.prompt_text_area.text = text
        self.prompt_text_area.selection = Selection.cursor(self.prompt_text_area.get_cursor_line_end_location())

    # def focus(self, scroll_visible: bool = True) -> Self:
    #     if self._ask is not None:
    #         self.question.focus()
    #     else:
    #         self.query(PromptTextArea).focus()
    #     return self

    def append(self, text: str) -> None:
        self.query_one(PromptTextArea).insert(text, maintain_selection_offset=False)

    def compose(self) -> ComposeResult:
        yield Flash()
        yield TextAreaAutoComplete("#input")
        with PromptContainer(id="prompt-container"):
            yield PromptInput(id="prompt-input")

        yield Analytics(id="analytics-panel")

    def watch_allow_input_submit(self, allow_input_submit: bool) -> None:
        self.set_class(not allow_input_submit, "hidden")
        self.disabled = not allow_input_submit
        self.app.conversation.scroll_to_latest_message()
