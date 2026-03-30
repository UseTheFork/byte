from dataclasses import dataclass
from operator import itemgetter
from typing import TYPE_CHECKING, Iterable, Self, Sequence

from textual import containers, getters, widgets
from textual.app import ComposeResult
from textual.binding import Binding
from textual.content import Content, Span
from textual.message import Message
from textual.reactive import var
from textual.widgets.option_list import Option

from byte.support import FuzzySearch
from byte.tui import AutocompleteOption, Messages
from byte.tui.widgets.columns import Columns

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class Autocompleter(containers.VerticalGroup, can_focus=False):
    """A widget to auto-complete slash commands."""

    @dataclass
    class Completed(Message):
        command: str

    CURSOR_BINDING_GROUP = Binding.Group(description="Select")
    BINDINGS = [
        Binding(
            "up",
            "cursor_up",
            "Cursor up",
            group=CURSOR_BINDING_GROUP,
            priority=True,
        ),
        Binding(
            "down",
            "cursor_down",
            "Cursor down",
            group=CURSOR_BINDING_GROUP,
            priority=True,
        ),
        Binding("enter", "submit", "Insert /command", priority=True),
        Binding("escape", "dismiss", "Dismiss", priority=True),
    ]

    DEFAULT_CSS = """
    SlashComplete {
        OptionList {
            height: auto;
        }
    }
    """

    app: ByteTUI

    input = getters.query_one(widgets.Input)
    option_list = getters.query_one(widgets.OptionList)

    autocomplete_options: var[list[AutocompleteOption]] = var(list[AutocompleteOption]())
    # type: str

    def __init__(
        self,
        autocomplete_options: Iterable[AutocompleteOption] | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.autocomplete_options = list(autocomplete_options) if autocomplete_options else []

        self.hints = {
            autocomplete_option.name: autocomplete_option.description
            for autocomplete_option in self.autocomplete_options
            if autocomplete_option.description
        }

        self.fuzzy_search = FuzzySearch(case_sensitive=False)

    def compose(self) -> ComposeResult:
        yield widgets.OptionList()

    def focus(self, scroll_visible: bool = False) -> Self:
        self.filter_options("")
        self.input.focus(scroll_visible)
        return self

    def on_mount(self) -> None:
        self.filter_options("")

    def on_descendant_blur(self) -> None:
        self.post_message(Messages.Dismiss(self))

    async def watch_autocomplete_option(self, autocomplete_options: list[AutocompleteOption]) -> None:
        self.hints = {
            slash_command.name: slash_command.description
            for slash_command in autocomplete_options
            if slash_command.description
        }

        self.filter_options(self.input.value)

    def filter_options(self, prompt: str) -> None:
        """Filter slash commands by the given prompt.

        Args:
            prompt: Text prompt.
        """
        prompt = prompt.lstrip("/").casefold().rstrip()

        self.app.byte["log"].info(prompt)

        columns = self.columns = Columns("auto", "flex")

        autocomplete_options = sorted(
            self.autocomplete_options,
            key=lambda autocomplete_option: autocomplete_option.name.casefold(),
        )
        deduplicated_slash_commands = {
            autocomplete_option.name: autocomplete_options for autocomplete_option in autocomplete_options
        }
        self.fuzzy_search.cache.grow(len(deduplicated_slash_commands))

        if prompt:
            slash_prompt = f"{prompt}"
            scores: list[tuple[float, Sequence[int], AutocompleteOption]] = [
                (
                    *self.fuzzy_search.match(prompt, autocomplete_option.name),
                    autocomplete_option,
                )
                for autocomplete_option in autocomplete_options
            ]

            scores = sorted(
                [
                    (
                        (score * 2 if slash_command.name.casefold().startswith(slash_prompt) else score),
                        highlights,
                        slash_command,
                    )
                    for score, highlights, slash_command in scores
                    if score
                ],
                key=itemgetter(0),
                reverse=True,
            )
        else:
            scores = [(1.0, [], autocomplete_option) for autocomplete_option in autocomplete_options]

        def make_row(autocomplete_option: AutocompleteOption, indices: Iterable[int]) -> tuple[Content, ...]:
            """Make a row for the Columns display.

            Args:
                slash_command: The slash command instance.
                indices: Indices of matching characters.

            Returns:
                A tuple of `Content` instances for use as a column row.
            """
            command = Content.styled(autocomplete_option.name, "$text-success")
            command = command.add_spans([Span(index + 1, index + 2, "underline not dim") for index in indices])
            return (command, Content.styled(autocomplete_option.description, "dim"))

        rows = [
            (
                columns.add_row(
                    *make_row(slash_command, indices),
                ),
                slash_command.name,
            )
            for _, indices, slash_command in scores
        ]
        self.option_list.set_options(Option(row, id=command_name) for row, command_name in rows)
        if self.display:
            self.option_list.highlighted = 0
        else:
            with self.option_list.prevent(widgets.OptionList.OptionHighlighted):
                self.option_list.highlighted = 0

    def action_cursor_down(self) -> None:
        self.option_list.action_cursor_down()

    def action_cursor_up(self) -> None:
        self.option_list.action_cursor_up()

    def action_dismiss(self) -> None:
        self.post_message(Messages.Dismiss(self))

    def action_submit(self) -> None:
        option_list = self.option_list
        if (option := option_list.highlighted_option) is not None:
            self.post_message(self.Completed(option.id or ""))
