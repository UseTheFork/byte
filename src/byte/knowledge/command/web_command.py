from argparse import Namespace

from byte import ByteArgumentParser, Command
from byte.cli import InputCancelledError
from byte.config import ByteConfigException
from byte.knowledge import SessionContextModel, SessionContextService
from byte.support.mixins import UserInteractive
from byte.support.utils import slugify
from byte.tui import InteractionService, Messages
from byte.tui.schemas import Answer
from byte.web import ChromiumService


class WebCommand(Command, UserInteractive):
    """Command to scrape web pages and convert them to markdown format.

    Fetches a webpage using headless Chrome, converts the HTML content to
    markdown, displays it for review, and optionally adds it to the LLM context.
    Usage: `/web https://example.com` -> scrapes and displays page as markdown
    """

    @property
    def name(self) -> str:
        return "web"

    @property
    def category(self) -> str:
        return "Session Context"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Fetch webpage using headless Chrome, convert HTML to markdown, display for review, and optionally add to LLM context",
        )
        parser.add_argument("url", help="URL to scrape")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute the web scraping command.

        Scrapes the provided URL, converts content to markdown, displays it
        in a formatted panel, and prompts user to add it to LLM context.

        Args:
                args: URL to scrape

        Usage: Called when user types `/web <url>`
        """

        self.emit_tui(Messages.AddUserInput(raw_args, command=self.name))

        session_context_service = self.app.make(SessionContextService)

        url = args.url

        try:
            chromium_service = self.app.make(ChromiumService)
            markdown_content = await chromium_service.do_scrape(url)
        except ByteConfigException as e:
            self.emit_tui(
                Messages.CreatePanel(
                    str(e),
                    title="Configuration Error",
                    border_style="error",
                )
            )
            return

        self.emit_tui(
            Messages.CreatePanel(
                str(markdown_content),
                f"Content: {url}",
            )
        )

        try:
            interaction_service = self.app.make(InteractionService)
            choice = await interaction_service.select(
                "Add this content to the LLM context?",
                [
                    Answer("Yes", "yes", True),
                    Answer("Clean with LLM", "clean"),
                    Answer("No", "no"),
                ],
            )
        except InputCancelledError:
            return

        if choice.value == "yes":
            await self.notify_success("Content added to context")

            key = slugify(url)
            model = self.app.make(SessionContextModel, type="web", key=key, content=markdown_content)
            session_context_service.add_context(model)

        elif choice.value == "clean":
            # console.print_info("Cleaning content with LLM...")

            # cleaner_agent = self.app.make(CleanerAgent)
            # result = await cleaner_agent.execute(
            #     f"# Extract only the relevant information from this web content:\n\n{markdown_content}",
            #     display_mode="thinking",
            # )

            # cleaned_content = result.get("cleaned_content", "")
            cleaned_content = None

            if cleaned_content:
                # console.print_success("Content cleaned and added to context")
                key = slugify(raw_args)
                model = self.app.make(SessionContextModel, type="web", key=key, content=cleaned_content)
                session_context_service.add_context(model)
            else:
                pass
                # console.print_warning("No cleaned content returned")
        else:
            await self.notify_warning("Content not added to context")
