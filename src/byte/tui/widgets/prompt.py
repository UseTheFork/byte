from dataclasses import dataclass

from textual import events, on
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import TextArea

# class PromptTextArea(HighlightedTextArea):
#     BINDING_GROUP_TITLE = "Prompt"

#     # app = getters.app(ToadApp)
#     auto_completes: var[list[Option]] = var(list)
#     multi_line = var(False, bindings=True)
#     shell_mode = var(False, bindings=True)
#     agent_ready: var[bool] = var(False)

#     class Submitted(Message):
#         def __init__(self, markdown: str) -> None:
#             self.markdown = markdown
#             super().__init__()

#     def on_mount(self) -> None:
#         self.highlight_cursor_line = False
#         self.hide_suggestion_on_blur = False

#     def on_key(self, event: events.Key) -> None:
#         if not self.shell_mode and self.cursor_location == (0, 0) and event.character in {"!", "$"}:
#             # self.post_message(self.RequestShellMode())
#             event.prevent_default()
#         elif self.shell_mode and event.key == "tab":
#             event.prevent_default()
#         elif event.key != "escape":
#             self.suggestions = None
#             self.suggestion = ""


# class Prompt(containers.VerticalGroup):
#     BINDINGS = [
#         Binding("escape", "dismiss", "Dismiss", show=False),
#     ]

#     prompt_container = getters.query_one("#prompt-container", Widget)
#     prompt_text_area = getters.query_one(PromptTextArea)
#     prompt_label = getters.query_one("#prompt", Label)
#     # current_directory = getters.query_one(CondensedPath)
#     # path_search = getters.query_one(PathSearch)
#     # slash_complete = getters.query_one(SlashComplete)
#     # question = getters.query_one(Question)
#     # mode_switcher = getters.query_one(ModeSwitcher)


# Credits to https://github.com/darrenburns/elia/blob/main/elia_chat/widgets/prompt_input.py
class Prompt(TextArea):
    @dataclass
    class PromptSubmitted(Message):
        text: str
        prompt_input: "Prompt"

    @dataclass
    class CursorEscapingTop(Message):
        pass

    @dataclass
    class CursorEscapingBottom(Message):
        pass

    BINDINGS = [
        Binding("ctrl+j,alt+enter", "submit_prompt", "Send message", key_display="^j"),
    ]

    submit_ready = reactive(True)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled, language="markdown")

    def on_key(self, event: events.Key) -> None:
        if self.cursor_location == (0, 0) and event.key == "up":
            event.prevent_default()
            self.post_message(self.CursorEscapingTop())
            event.stop()
        elif self.cursor_at_end_of_text and event.key == "down":
            event.prevent_default()
            self.post_message(self.CursorEscapingBottom())
            event.stop()

    def watch_submit_ready(self, submit_ready: bool) -> None:
        self.set_class(not submit_ready, "-submit-blocked")

    def on_mount(self):
        self.border_title = "Enter your message..."

    @on(TextArea.Changed)
    async def prompt_changed(self, event: TextArea.Changed) -> None:
        text_area = event.text_area
        if text_area.text.strip() != "":
            text_area.border_subtitle = "(^j) Send message"
        else:
            text_area.border_subtitle = None

        text_area.set_class(text_area.wrapped_document.height > 1, "multiline")

        # TODO - when the height of the textarea changes
        #  things don't appear to refresh correctly.
        #  I think this may be a Textual bug.
        #  The refresh below should not be required.
        # self.parent.refresh()

    def action_submit_prompt(self) -> None:
        if self.text.strip() == "":
            self.notify("Cannot send empty message!")
            return

        if self.submit_ready:
            message = self.PromptSubmitted(self.text, prompt_input=self)
            self.clear()
            self.post_message(message)
        else:
            self.app.bell()
            self.notify("Please wait for response to complete.")
