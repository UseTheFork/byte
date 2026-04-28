from rich.console import RenderableType
from textual.widgets import Static


class Bootbox(Static):
    #     MESSAGE = """
    # To get started, type a message in the box at the top of the
    # screen and press [b u]ctrl+j[/] or [b u]alt+enter[/] to send it.

    # Change the model and system prompt by pressing [b u]ctrl+o[/].

    # Make sure you've set any required API keys first (e.g. [b]OPENAI_API_KEY[/])!

    # If you have any issues or feedback, please let me know [@click='open_issues'][b r]on GitHub[/][/]!

    # Finally, please consider starring the repo and sharing it with your friends and colleagues!

    # [@click='open_repo'][b r]https://github.com/darrenburns/elia[/][/]
    # """

    #     BORDER_TITLE = "Welcome to Byte!"

    DEFAULT_CSS = """
    Bootbox {
        height: auto;
        width: 100%;
        min-width: 12;
        max-width: 1fr;
        margin: 0 1;
        padding: 0 2;
        border: round $primary;
    }
    """

    def __init__(
        self,
        message: str,
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
        self.message = message

    def render(self) -> RenderableType:
        return self.message
