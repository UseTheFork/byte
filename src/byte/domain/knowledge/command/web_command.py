from argparse import Namespace

from byte.core.exceptions import ByteConfigException
from byte.core.mixins.user_interactive import UserInteractive
from byte.core.utils import slugify
from byte.domain.agent.implementations.cleaner.agent import CleanerAgent
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.rich.markdown import Markdown
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.knowledge.models import SessionContextModel
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
        console = await self.make(ConsoleService)
        session_context_service = await self.make(SessionContextService)

        url = args.url

        try:
            chromium_service = await self.make(ChromiumService)
            markdown_content = await chromium_service.do_scrape(url)
        except ByteConfigException as e:
            console.print_error_panel(
                str(e),
                title="Configuration Error",
            )
            return

        markdown_rendered = Markdown(markdown_content)
        console.print_panel(
            markdown_rendered,
            title=f"Content: {url}",
        )

        choice = await self.prompt_for_select_numbered(
            "Add this content to the LLM context?",
            choices=["Yes", "Clean with LLM", "No"],
            default=1,
        )

        if choice == "Yes":
            console.print_success("Content added to context")

            key = slugify(url)
            model = await self.make(SessionContextModel, type="web", key=key, content=markdown_content)
            session_context_service.add_context(model)

        elif choice == "Clean with LLM":
            console.print_info("Cleaning content with LLM...")

            cleaner_agent = await self.make(CleanerAgent)
            result = await cleaner_agent.execute(
                f"# Extract only the relevant information from this web content:\n\n{markdown_content}",
                display_mode="thinking",
            )

            cleaned_content = result.get("cleaned_content", "")

            if cleaned_content:
                console.print_success("Content cleaned and added to context")
                key = slugify(args)
                model = await self.make(SessionContextModel, type="web", key=key, content=cleaned_content)
                session_context_service.add_context(model)
            else:
                console.print_warning("No cleaned content returned")
        else:
            console.print_warning("Content not added to context")
