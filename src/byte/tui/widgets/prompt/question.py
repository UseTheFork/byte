from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Callable

from textual import containers, events, getters, on, widgets
from textual.app import ComposeResult
from textual.binding import Binding
from textual.content import Content
from textual.message import Message
from textual.reactive import reactive, var
from textual.widget import Widget

from byte.tui import Messages
from byte.tui.schemas import Answer, Ask

type Options = list[Answer]


# Credits: https://github.com/batrachianai/toad/blob/main/src/toad/widgets/question.py
class NonSelectableLabel(widgets.Label):
    ALLOW_SELECT = False


class Option(containers.HorizontalGroup):
    @dataclass
    class Selected(Message):
        """The option was selected."""

        index: int

    ALLOW_SELECT = False
    DEFAULT_CSS = """
    Option {

        &:hover {
            background: $boost;
        }
        color: $text-muted;
        #caret {
            visibility: hidden;
            padding: 0 1;
        }
        #index {
            padding-right: 1;
        }
        #label {
            width: 1fr;
        }
        &.-active {            
            color: $text-accent;
            #caret {
                visibility: visible;
            }
        }
        &.-selected {
            opacity: 0.5;
        }
        &.-active.-selected {
            opacity: 1.0;
            background: transparent;
            color: $text-accent;            
            #label {
                text-style: underline;
            }
            #caret {
                visibility: hidden;
            }
        }
    }
    """

    selected: reactive[bool] = reactive(False, toggle_class="-selected")

    def __init__(self, index: int, content: Content, key: str | None, classes: str = "") -> None:
        super().__init__(classes=classes)
        self.index = index
        self.content = content
        self.key = key

    def compose(self) -> ComposeResult:
        key = self.key
        yield NonSelectableLabel("❯", id="caret")  # noqa: RUF001
        if key:
            yield NonSelectableLabel(Content.styled(f"{key}", "b"), id="index")
        else:
            yield NonSelectableLabel(Content(" "), id="index")

        yield NonSelectableLabel(self.content, id="label")

    def on_click(self, event: events.Click) -> None:
        event.stop()
        self.post_message(self.Selected(self.index))


class Question(containers.VerticalGroup, can_focus=True):
    """A text question with a menu of responses."""

    _result_future: asyncio.Future[Answer] | None = None

    BINDING_GROUP_TITLE = "Question"
    ALLOW_SELECT = False
    CURSOR_GROUP = Binding.Group("Cursor", compact=True)
    BINDINGS = [
        Binding(
            "up",
            "selection_up",
            "Up",
            group=CURSOR_GROUP,
        ),
        Binding(
            "down",
            "selection_down",
            "Down",
            group=CURSOR_GROUP,
        ),
        Binding(
            "enter",
            "select",
            "Select",
        ),
    ]

    DEFAULT_CSS = """
    Question {
        width: 1fr;
        height: auto;
        padding: 0 1; 
        background: transparent;
        #title {
            margin-bottom: 1;
            color: $text-primary;
        }
        #question-container {
            margin-bottom: 1;
        }        

        
        #option-container.-blink Option.-active #caret {
            opacity: 0.2;
        }

        &:blur {
            #index {
                opacity: 0.3;
            }
            #caret {
                opacity: 0.3;
            }
        }
    }
    """

    title: var[str] = var("")
    options: var[Options] = var([])

    selection: reactive[int] = reactive(0, init=False)
    selected: var[bool] = var(False, toggle_class="-selected")

    option_container = getters.query_one("#option-container", containers.VerticalGroup)

    def __init__(
        self,
        title: str = "Ask and you will receive",
        get_content: Callable[[], Widget] | None = None,
        options: Options | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.set_reactive(Question.title, title)
        self.set_reactive(Question.options, options or [])

    def update(self, ask: Ask) -> None:
        self.title = ask.question
        self.options = ask.options
        self._result_future = ask.result_future
        self.selection = 0
        self.selected = False
        self.refresh(recompose=True, layout=True)

    def compose(self) -> ComposeResult:
        with containers.VerticalGroup(id="contents"):
            if self.title:
                yield widgets.Label(self.title, id="title", markup=False)

        with containers.VerticalGroup(id="option-container"):
            for index, answer in enumerate(self.options):
                active = index == self.selection
                yield Option(
                    index,
                    Content(answer.text),
                    None,
                    classes="-active" if active else "",
                ).data_bind(Question.selected)

    def watch_selection(self, old_selection: int, new_selection: int) -> None:
        self.query("#option-container > .-active").remove_class("-active")
        if new_selection >= 0:
            self.query_one("#option-container").children[new_selection].add_class("-active")

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if self.selected and action in ("selection_up", "selection_down"):
            return False
        return True

    def action_selection_up(self) -> None:
        self.selection = max(0, self.selection - 1)

    def action_selection_down(self) -> None:
        self.selection = min(len(self.options) - 1, self.selection + 1)

    def action_select(self) -> None:
        answer = self.options[self.selection]

        # Resolve the future if present
        if self._result_future and not self._result_future.done():
            self._result_future.set_result(answer)

        # Still post message for other listeners
        self.post_message(Messages.Answer(index=self.selection, answer=answer))
        self.selected = True

    @on(Option.Selected)
    def on_option_selected(self, event: Option.Selected) -> None:
        event.stop()
        if not self.selected:
            self.selection = event.index
