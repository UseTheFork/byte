from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Self

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
from byte.cli import CommandRegistry
from byte.tui import Messages
from byte.tui.schemas import AutocompleteOption
from byte.tui.widgets.autocompleter import Autocompleter
from byte.tui.widgets.flash import Flash
from byte.tui.widgets.highlighted_textarea import HighlightedTextArea
from byte.tui.widgets.question import Ask, Question

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class InvokeFileSearch(Message):
    pass


class InvokeSlashComplete(Message):
    pass


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

    # auto_completes: var[list[Option]] = var(list)
    multi_line = var(False, bindings=True)
    agent_ready: var[bool] = var(False)

    suggestions: var[list[str] | None] = var(None)
    suggestions_index: var[int] = var(0)

    project_path = var(Path())

    autocomplete_options: var[list[Command]] = var([])

    slash_command_prefixes: var[tuple[str, ...]] = var(())

    # def watch_slash_commands(self, slash_commands: list[Command]) -> None:
    #     """A tuple of slash commands for performance reasons (used with `str.startswith`)."""
    #     self.slash_command_prefixes = tuple([f"/{slash_command.name}" for slash_command in slash_commands])

    # def highlight_slash_command(self, text: str) -> Content:
    #     """Override slash command highlighting."""

    #     if text.startswith(self.slash_command_prefixes):
    #         content = Content(text)
    #         for slash_command in self.slash_commands:
    #             # Check with the / prefix
    #             if text.startswith(f"/{slash_command.name} "):
    #                 content = content.stylize("$text-success", 0, len(slash_command.name) + 1)  # +1 for the /
    #                 if (
    #                     slash_command.description and len(text) - (len(slash_command.name) + 2) == 0
    #                 ):  #  +2 for / and space
    #                     content += Content.styled(slash_command.description, "$text-secondary 70%")
    #                 break
    #         return content
    #     return Content(text)

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

    def action_submit(self) -> None:
        self.post_message(Messages.UserInputSubmitted(self.text))
        self.clear()

    def action_newline(self) -> None:
        self.insert("\n")

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

            if x > 0 and x <= len(line) and line[x - 1] == "@":
                remaining_line = line[x + 1 :]
                if not remaining_line or remaining_line[0].isspace():
                    self.post_message(InvokeFileSearch())


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
    PROMPT_SHELL = Content.styled("$", "$text-primary")
    PROMPT_AI = Content.styled("❯", "$text-secondary")  # noqa: RUF001
    PROMPT_MULTILINE = Content.styled("☰", "$text-secondary")

    prompt_container = getters.query_one("#prompt-container", Widget)
    prompt_text_area = getters.query_one(PromptTextArea)
    prompt_label = getters.query_one("#prompt", Label)
    question = getters.query_one(Question)

    auto_completer = getters.query_one(Autocompleter)

    # current_directory = getters.query_one(CondensedPath)
    # path_search = getters.query_one(PathSearch)
    # question = getters.query_one(Question)
    # mode_switcher = getters.query_one(ModeSwitcher)

    autocomplete_options: var[list[AutocompleteOption]] = var(list[AutocompleteOption]())
    show_auto_completer = var(False, toggle_class="-show-auto-complete", bindings=True)

    multi_line = var(False)

    project_path = var(Path, init=False)
    working_directory = var("")
    agent_info = var(Content(""))
    _ask: var[Ask | None] = var(None)
    # plan: var[list[Plan.Entry]]
    agent_ready: var[bool] = var(True)
    # current_mode: var[Mode | None] = var(None)
    # modes: var[dict[str, Mode] | None] = var(None)
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
        self.post_message(Messages.UserInputChanged(text))

        if self.show_auto_completer:
            self.auto_completer.filter_options(text)

        self.multi_line = "\n" in text or "```" in text

        self.update_prompt()

    @on(InvokeSlashComplete)
    def on_invoke_auto_completer_complete(self, event: InvokeSlashComplete) -> None:
        event.stop()

        command_registry = self.app.byte.make(CommandRegistry)
        all_commands = command_registry.get_all_commands()
        self.autocomplete_options = [
            AutocompleteOption(name=f"/{command.name}", description=command.description, type="command")
            for command in all_commands
        ]

        self.show_auto_completer = True

    @on(Messages.PromptSuggestion)
    def on_prompt_suggestion(self, event: Messages.PromptSuggestion) -> None:
        event.stop()
        self.prompt_text_area.suggestion = event.suggestion

    @on(Autocompleter.Completed)
    def on_auto_completer_complete_completed(self, event: Autocompleter.Completed) -> None:
        self.app.byte["log"].info("on_auto_completer_complete_completed")
        self.app.byte["log"].info(event)
        self.prompt_text_area.clear()
        self.prompt_text_area.insert(f"{event.command} ")
        self.prompt_text_area.suggestion = ""
        # TODO: This should check the type of completion that happend if it's a command completion we need to switch the autocompleter to use that commands options.

        self.focus()

    @on(Messages.Dismiss)
    def on_dismiss(self, event: Messages.Dismiss) -> None:
        event.stop()
        if event.widget is self.auto_completer and self.show_auto_completer:
            self.show_auto_completer = False
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

    def on_key(self, event: events.Key) -> None:
        self.app.byte["log"].info("prompt on_key")
        self.app.byte["log"].info(event)

        if event.key == "up" and self.show_auto_completer:
            event.prevent_default()
            self.auto_completer.action_cursor_up()
            event.stop()
        elif event.key == "down" and self.show_auto_completer:
            event.prevent_default()
            self.auto_completer.action_cursor_down()
            event.stop()
        elif event.key == "tab" and self.show_auto_completer:
            event.prevent_default()
            self.auto_completer.action_submit()
            event.stop()

    def compose(self) -> ComposeResult:
        # yield PathSearch(self.project_path).data_bind(root=Prompt.project_path)
        yield Flash()
        yield Autocompleter().data_bind(autocomplete_options=Prompt.autocomplete_options)
        with PromptContainer(id="prompt-container"):
            yield Question()
            with containers.HorizontalGroup(id="text-prompt"):
                yield Label(self.PROMPT_AI, id="prompt", markup=False)
                yield PromptTextArea().data_bind(
                    multi_line=Prompt.multi_line,
                    agent_ready=Prompt.agent_ready,
                    project_path=Prompt.project_path,
                    autocomplete_options=Prompt.autocomplete_options,
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
        elif self.show_auto_completer:
            self.show_auto_completer = False
        else:
            raise SkipAction
