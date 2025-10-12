from rich.console import Console
from rich.markdown import Markdown

from byte.core.mixins.user_interactive import UserInteractive
from byte.core.utils import slugify
from byte.domain.agent.implementations.cleaner.agent import CleanerAgent
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
			console.print("[info]Cleaning content with LLM...[/info]")

			cleaner_agent = await self.make(CleanerAgent)
			result = await cleaner_agent.execute(
				{
					"messages": [
						(
							"user",
							f"Please extract only the relevant information from this web content:\n\n{markdown_content}",
						)
					],
					"project_inforamtion_and_context": [],
				},
				display_mode="thinking",
			)

			cleaned_content = result.get("cleaned_content", "")

			if cleaned_content:
				console.print("[success]Content cleaned and added to context[/success]")
				key = slugify(args)
				session_context_service.add_context(key, cleaned_content)
			else:
				console.print("[warning]No cleaned content returned[/warning]")
		else:
			console.print("[info]Content not added to context[/info]")
