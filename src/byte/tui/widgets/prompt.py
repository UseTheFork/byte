import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Self

from textual import containers, events, getters, on
from textual.actions import SkipAction
from textual.app import ComposeResult
from textual.binding import Binding
from textual.content import Content
from textual.message import Message
from textual.reactive import var
from textual.widget import Widget
from textual.widgets import Label, TextArea
from textual.widgets.text_area import Selection

from byte import Command
from byte.tui import Messages
from byte.tui.widgets.flash import Flash
from byte.tui.widgets.highlighted_textarea import HighlightedTextArea
from byte.tui.widgets.question import Ask, Question
from byte.tui.widgets.slash_complete import SlashComplete


class InvokeFileSearch(Message):
    pass


class InvokeSlashComplete(Message):
    pass


class AgentInfo(Label):
    pass


class ModeInfo(Label):
    pass


class PromptTextArea(HighlightedTextArea):
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

    # app = getters.app(ToadApp)
    auto_completes: var[list[Option]] = var(list)
    multi_line = var(False, bindings=True)
    agent_ready: var[bool] = var(False)

    suggestions: var[list[str] | None] = var(None)
    suggestions_index: var[int] = var(0)

    project_path = var(Path())

    slash_commands: var[list[Command]] = var([])
    slash_command_prefixes: var[tuple[str, ...]] = var(())

    class Submitted(Message):
        def __init__(self, markdown: str) -> None:
            self.markdown = markdown
            super().__init__()

    def watch_slash_commands(self, slash_commands: list[Command]) -> None:
        """A tuple of slash commands for performance reasons (used with `str.startswith`)."""
        self.slash_command_prefixes = tuple([slash_command.name for slash_command in slash_commands])

    def highlight_slash_command(self, text: str) -> Content:
        """Override slash command highlighting."""

        if text.startswith(self.slash_command_prefixes):
            content = Content(text)
            for slash_command in self.slash_commands:
                if text.startswith(slash_command.name + " "):
                    content = content.stylize("$text-success", 0, len(slash_command.name))
                    if slash_command.description and len(text) - (len(slash_command.name) + 1) == 0:
                        content += Content.styled(slash_command.description, "$text-secondary 70%")
                    break
            return content
        return Content(text)

    def on_mount(self) -> None:
        self.highlight_cursor_line = False
        self.hide_suggestion_on_blur = False

    def on_key(self, event: events.Key) -> None:
        # if not self.shell_mode and self.cursor_location == (0, 0) and event.character in {"!", "$"}:
        #     # self.post_message(self.RequestShellMode())
        #     event.prevent_default()
        if event.key != "escape":
            self.suggestions = None
            self.suggestion = ""

    def update_suggestion(self) -> None:
        prompt = self.query_ancestor(Prompt)

        if self.selection.start == self.selection.end and self.text.startswith("/"):
            return

        # if self.shell_mode and self.cursor_at_end_of_text and "\n" not in self.text:
        #     if prompt.complete_callback is not None:
        #         if completes := prompt.complete_callback(self.text):
        #             if self.text not in completes:
        #                 self.suggestion = completes[-1]

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "newline" and self.multi_line:
            return False
        if action == "submit" and self.multi_line:
            return False
        if action == "multiline_submit":
            return self.multi_line
        return True

    def action_multiline_submit(self) -> None:
        if not self.agent_ready:
            self.app.bell()
            self.post_message(
                Messages.Flash(
                    "Agent is not ready. Please wait while the agent connects…",
                    "error",
                )
            )
            return
        self.post_message(Messages.UserInputSubmitted(self.text))
        self.clear()

    def action_newline(self) -> None:
        self.insert("\n")

    def action_submit(self) -> None:
        # TODO: DO we need this does this belong here?
        if not self.agent_ready:
            self.app.bell()
            self.post_message(
                Messages.Flash(
                    "Agent is not ready. Please wait while the agent connects…",
                    "error",
                )
            )
            return
        if self.suggestion:
            if " " not in self.text:
                self.insert(self.suggestion + " ")
            else:
                prompt = self.query_ancestor(Prompt)
                last_token = shlex.split(self.text + self.suggestion)[-1]
                last_token_path = Path(prompt.working_directory) / last_token
                if last_token_path.is_dir():
                    self.insert(self.suggestion)
                else:
                    self.insert(self.suggestion + " ")
                self.suggestion = ""
            return

        self.app.byte_app["log"].info(5)

        self.post_message(Messages.UserInputSubmitted(self.text))
        self.clear()

    def action_cursor_up(self, select: bool = False):
        if self.selection.is_empty and not select:
            row, _column = self.selection[0]
            if row == 0:
                self.post_message(Messages.HistoryMove(-1, self.text))
                return
        super().action_cursor_up(select)

    def action_cursor_down(self, select: bool = False):
        if self.selection.is_empty and not select:
            row, _column = self.selection[0]
            if row == (self.wrapped_document.height - 1):
                self.post_message(Messages.HistoryMove(+1, self.text))
                return
        super().action_cursor_down(select)

    def action_cursor_line_end(self, select: bool = False) -> None:
        """Move the cursor to the end of the line."""
        if not self._has_cursor:
            self.scroll_end()
            return
        location = self.get_cursor_line_end_location()
        if location == self.cursor_location:
            pass
            # TODO: THIS.

            # If the cursor is already at the end, then we assume the user wants to
            # scroll the conversation to the end
            # from byte.tui.widgets.chatbox import Chatbox

            # self.query_ancestor(Chatbox).window.anchor()
        else:
            self.move_cursor(location, select=select)

    # async def action_tab_complete(self) -> None:
    #     if not self.shell_mode:
    #         return

    #     import shlex

    #     prompt = self.query_ancestor(Prompt)

    #     if not self.cursor_at_end_of_text:
    #         return

    #     _cursor_row, cursor_column = prompt.prompt_text_area.selection.end
    #     pre_complete = self.text[:cursor_column]
    #     post_complete = self.text[cursor_column:]
    #     shlex_tokens = shlex.split(pre_complete)
    #     if not shlex_tokens:
    #         return

    #     command = shlex_tokens[0]

    #     exclude_node_type: Literal[file] | Literal[dir] | None = None
    #     if command in self.app.settings.get("shell.directory_commands", str).splitlines():
    #         exclude_node_type = "file"
    #     elif command in self.app.settings.get("shell.file_commands", str).splitlines():
    #         exclude_node_type = "dir"

    #     tab_complete, suggestions = await self.path_complete(
    #         Path(prompt.working_directory),
    #         shlex_tokens[-1],
    #         exclude_type=exclude_node_type,
    #     )

    #     if tab_complete is not None:
    #         shlex_tokens = shlex_tokens[:-1] + [shlex_tokens[-1] + tab_complete]
    #         path_component = Path(prompt.working_directory) / shlex_tokens[-1]
    #         if path_component.is_file():
    #             spaces = " "
    #         else:
    #             spaces = ""

    #         self.clear()
    #         self.insert(" ".join(token.replace(" ", "\\ ") for token in shlex_tokens) + post_complete + spaces)
    #         self.suggestions = None
    #     else:
    #         if suggestions != self.suggestions:
    #             self.suggestions = suggestions or None
    #             self.suggestions_index = 0
    #             if suggestions:
    #                 self.suggestion = suggestions[0]
    #         elif self.suggestions:
    #             self.suggestions_index = (self.suggestions_index + 1) % len(self.suggestions)
    #             self.suggestion = self.suggestions[self.suggestions_index]

    async def watch_selection(self, previous_selection: Selection, selection: Selection) -> None:
        if previous_selection == selection:
            return
        if selection.start == selection.end:
            previous_y, previous_x = previous_selection.end
            y, x = selection.end
            if y == previous_y:
                direction = -1 if x < previous_x else +1
            else:
                direction = 0
            line = self.document.get_line(y)

            if y == 0 and x == 1 and direction == +1 and line and line[0] == "/":
                self.post_message(InvokeSlashComplete())
                return

            if y == 0 and line and line[0] == "/" and direction == -1:
                if line in self.slash_command_prefixes:
                    self.selection = Selection((0, 0), (0, len(line)))
                    return

            # for _path, start, end in extract_paths_from_prompt(line):
            #     if x > start and x < end:
            #         self.selection = Selection((y, start), (y, end))
            #         break
            #     if direction == -1 and x == end:
            #         self.selection = Selection((y, start), (y, end))
            #         break

            # if x > 0 and x <= len(line) and line[x - 1] == "@":
            #     remaining_line = line[x + 1 :]
            #     if not remaining_line or remaining_line[0].isspace():
            #         self.post_message(InvokeFileSearch())


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
        Binding("escape", "dismiss", "Dismiss", show=False),
    ]

    PROMPT_NULL = " "
    PROMPT_SHELL = Content.styled("$", "$text-primary")
    PROMPT_AI = Content.styled("❯", "$text-secondary")  # noqa: RUF001
    PROMPT_MULTILINE = Content.styled("☰", "$text-secondary")

    prompt_container = getters.query_one("#prompt-container", Widget)
    prompt_text_area = getters.query_one(PromptTextArea)
    prompt_label = getters.query_one("#prompt", Label)
    question = getters.query_one(Question)

    # current_directory = getters.query_one(CondensedPath)
    # path_search = getters.query_one(PathSearch)
    slash_complete = getters.query_one(SlashComplete)
    # question = getters.query_one(Question)
    # mode_switcher = getters.query_one(ModeSwitcher)

    slash_commands: var[list[Command]] = var(list)
    multi_line = var(False)
    show_path_search = var(False, toggle_class="-show-path-search", bindings=True)
    show_slash_complete = var(False, toggle_class="-show-slash-complete", bindings=True)
    project_path = var(Path, init=False)
    working_directory = var("")
    agent_info = var(Content(""))
    _ask: var[Ask | None] = var(None)
    # plan: var[list[Plan.Entry]]
    agent_ready: var[bool] = var(True)
    # current_mode: var[Mode | None] = var(None)
    # modes: var[dict[str, Mode] | None] = var(None)
    status: var[str] = var("")

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
        prompt_message = " yes?"
        self.prompt_text_area.placeholder = Content.assemble(
            f"{prompt_message}\t".expandtabs(8),
            ("▌!▐", "r"),
            " shell ",
            ("▌/▐", "r"),
            " commands ",
            ("▌@▐", "r"),
            " files",
        )
        self.prompt_text_area.highlight_language = "markdown"

    def focus(self, scroll_visible: bool = True) -> Self:
        if self._ask is not None:
            self.question.focus()
        else:
            self.query(HighlightedTextArea).focus()
        return self

    def append(self, text: str) -> None:
        self.query_one(HighlightedTextArea).insert(text, maintain_selection_offset=False)

    @on(TextArea.Changed)
    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        text = event.text_area.text

        self.multi_line = "\n" in text or "```" in text

        # TODO: This.
        # if not self.multi_line and self.likely_shell:
        #     self.shell_mode = True

        self.update_prompt()

    @on(InvokeSlashComplete)
    def on_invoke_slash_complete(self, event: InvokeSlashComplete) -> None:
        event.stop()
        self.show_slash_complete = True

    @on(Messages.PromptSuggestion)
    def on_prompt_suggestion(self, event: Messages.PromptSuggestion) -> None:
        event.stop()
        self.prompt_text_area.suggestion = event.suggestion

    @on(SlashComplete.Completed)
    def on_slash_complete_completed(self, event: SlashComplete.Completed) -> None:
        self.prompt_text_area.clear()
        self.prompt_text_area.insert(f"{event.command} ")
        self.prompt_text_area.suggestion = ""
        self.focus()

    @on(Messages.Dismiss)
    def on_dismiss(self, event: Messages.Dismiss) -> None:
        event.stop()
        if event.widget is self.slash_complete and self.show_slash_complete:
            self.show_slash_complete = False
            self.prompt_text_area.suggestion = ""
            self.focus()
            # TODO: This
        # elif event.widget is self.path_search and self.show_path_search:
        #     self.show_path_search = False
        #     self.focus()

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

    def suggest(self, suggestion: str) -> None:
        if suggestion.startswith(self.text) and self.text != suggestion:
            self.prompt_text_area.suggestion = suggestion[len(self.text) :]

    def compose(self) -> ComposeResult:
        # yield PathSearch(self.project_path).data_bind(root=Prompt.project_path)
        yield Flash()
        yield SlashComplete().data_bind(slash_commands=Prompt.slash_commands)
        with PromptContainer(id="prompt-container"):
            yield Question()
            with containers.HorizontalGroup(id="text-prompt"):
                yield Label(self.PROMPT_AI, id="prompt", markup=False)
                yield PromptTextArea().data_bind(
                    multi_line=Prompt.multi_line,
                    agent_ready=Prompt.agent_ready,
                    project_path=Prompt.project_path,
                    slash_commands=Prompt.slash_commands,
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
        if self.prompt_text_area.suggestion:
            self.prompt_text_area.suggestion = ""
            return
        elif self.show_slash_complete:
            self.show_slash_complete = False
        else:
            raise SkipAction


# /////////////////////////////////////


# # Credits to https://github.com/darrenburns/elia/blob/main/elia_chat/widgets/prompt_input.py
# class Prompt(TextArea):
#     @dataclass
#     class PromptSubmitted(Message):
#         text: str
#         prompt_input: "Prompt"

#     @dataclass
#     class CursorEscapingTop(Message):
#         pass

#     @dataclass
#     class CursorEscapingBottom(Message):
#         pass

#     BINDINGS = [
#         Binding("ctrl+j,alt+enter", "submit_prompt", "Send message", key_display="^j"),
#     ]

#     submit_ready = reactive(True)

#     def __init__(
#         self,
#         name: str | None = None,
#         id: str | None = None,
#         classes: str | None = None,
#         disabled: bool = False,
#     ) -> None:
#         super().__init__(name=name, id=id, classes=classes, disabled=disabled, language="markdown")

#     def on_key(self, event: events.Key) -> None:
#         if self.cursor_location == (0, 0) and event.key == "up":
#             event.prevent_default()
#             self.post_message(self.CursorEscapingTop())
#             event.stop()
#         elif self.cursor_at_end_of_text and event.key == "down":
#             event.prevent_default()
#             self.post_message(self.CursorEscapingBottom())
#             event.stop()

#     def watch_submit_ready(self, submit_ready: bool) -> None:
#         self.set_class(not submit_ready, "-submit-blocked")

#     def on_mount(self):
#         self.border_title = "Enter your message..."

#     @on(TextArea.Changed)
#     async def prompt_changed(self, event: TextArea.Changed) -> None:
#         text_area = event.text_area
#         if text_area.text.strip() != "":
#             text_area.border_subtitle = "(^j) Send message"
#         else:
#             text_area.border_subtitle = None

#         text_area.set_class(text_area.wrapped_document.height > 1, "multiline")

#         # TODO - when the height of the textarea changes
#         #  things don't appear to refresh correctly.
#         #  I think this may be a Textual bug.
#         #  The refresh below should not be required.
#         # self.parent.refresh()

#     def action_submit_prompt(self) -> None:
#         if self.text.strip() == "":
#             self.notify("Cannot send empty message!")
#             return

#         if self.submit_ready:
#             message = self.PromptSubmitted(self.text, prompt_input=self)
#             self.clear()
#             self.post_message(message)
#         else:
#             self.app.bell()
#             self.notify("Please wait for response to complete.")
