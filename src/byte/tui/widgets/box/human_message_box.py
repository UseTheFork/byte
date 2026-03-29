from rich.markdown import Markdown
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.content import Content
from textual.widget import Widget
from textual.widgets import Label


class HumanMessageBox(Widget, can_focus=False):
    PROMPT_AI = Content.styled("❯", "$text-secondary")  # noqa: RUF001

    def __init__(
        self,
        content: str,
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
        self.content: str = content

    @property
    def markdown(self) -> Markdown:
        """Return the content as a Rich Markdown object."""

        return Markdown(self.content)
        # return Markdown(content, code_theme=self.app.launch_config.message_code_theme)

    def compose(self) -> ComposeResult:
        # yield PathSearch(self.project_path).data_bind(root=Prompt.project_path)
        with HorizontalGroup(classes="text-prompt"):
            yield Label(self.PROMPT_AI, classes="carrot", markup=False)
            yield Label(self.markdown, classes="message", markup=False)
