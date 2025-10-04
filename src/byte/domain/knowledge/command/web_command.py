from rich.console import Console
from rich.markdown import Markdown

from byte.core.mixins.user_interactive import UserInteractive
from byte.core.utils import slugify
from byte.domain.cli.rich.panel import Panel
from byte.domain.cli.service.command_registry import Command
from byte.domain.knowledge.service.session_context_service import SessionContextService
from byte.domain.web.service.chromium_service import ChromiumService


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
    def description(self) -> str:
        return "Scrape a webpage and convert it to markdown"

    async def execute(self, args: str) -> None:
        """Execute the web scraping command.

        Scrapes the provided URL, converts content to markdown, displays it
        in a formatted panel, and prompts user to add it to LLM context.

        Args:
            args: URL to scrape

        Usage: Called when user types `/web <url>`
        """
        console = await self.make(Console)

        session_context_service = await self.make(SessionContextService)

        chromium_service = await self.make(ChromiumService)
        markdown_content = await chromium_service.do_scrape(args)

        markdown_rendered = Markdown(markdown_content)
        console.print(
            Panel(
                markdown_rendered,
                title=f"Content: {args}",
            )
        )

        choice = await self.prompt_for_select_numbered(
            "Add this content to the LLM context?",
            choices=["Yes", "Clean with LLM", "No"],
            default=1,
        )

        if choice == "Yes":
            console.print("[success]Content added to context[/success]")

            key = slugify(args)
            session_context_service.add_context(key, markdown_content)

        elif choice == "Clean with LLM":
            console.print(
                "[success]Content will be cleaned with LLM and added to context[/success]"
            )
        else:
            console.print("[info]Content not added to context[/info]")
