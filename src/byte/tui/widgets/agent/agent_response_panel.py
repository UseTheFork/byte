from __future__ import annotations

from typing import TYPE_CHECKING

from textual import getters
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.reactive import var
from textual.widgets import Markdown

from byte.tui.widgets.ui.rune_spinner import RuneSpinner
from byte.tui.widgets.ui.text_rule import TextRule

if TYPE_CHECKING:
    from byte.tui import ByteTUI


class AgentResponsePanel(VerticalGroup):
    BINDINGS = []

    app: ByteTUI

    rune_spinner = getters.query_one("#rune_spinner", RuneSpinner)
    heading = getters.query_one(TextRule)
    agent_response_widget = getters.query_one("#agent_response", Markdown)

    response: var[str] = var("")

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def compose(self) -> ComposeResult:
        yield TextRule(classes="text-primary hidden")
        yield RuneSpinner(id="rune_spinner")
        yield Markdown(id="agent_response")
