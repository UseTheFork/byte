from textwrap import dedent

from byte.core.array_store import ArrayStore
from byte.core.config.config import BYTE_DIR
from byte.core.event_bus import Payload
from byte.core.service.base_service import Service


class ConventionContextService(Service):
	"""Service for loading and managing project conventions from markdown files.

	Uses ArrayStore to manage convention documents loaded from the conventions
	directory. Conventions are automatically loaded during boot and injected
	into the prompt context.
	Usage: `service = ConventionContextService(container)`
	"""

	async def boot(self) -> None:
		"""Load convention files from the conventions directory into ArrayStore.

		Checks for a 'conventions' directory in BYTE_DIR and loads all .md files
		found there. Each file is stored in the ArrayStore with its filename as the key.
		Usage: `await service.boot()`
		"""
		self.conventions = ArrayStore()
		conventions_dir = BYTE_DIR / "conventions"

		if not conventions_dir.exists() or not conventions_dir.is_dir():
			return

		# Iterate over all .md files in the conventions directory
		for md_file in sorted(conventions_dir.glob(pattern="*.md", case_sensitive=False)):
			try:
				content = md_file.read_text(encoding="utf-8")
				# Format as a document with filename header and separator
				formatted_doc = f"## Convention: {md_file.name}\n\n{content}"
				self.conventions.add(md_file.name, formatted_doc)
			except Exception:
				pass

	async def add_project_context_hook(self, payload: Payload) -> Payload:
		"""Inject convention context into the prompt state.

		Aggregates all stored convention documents and adds them to the
		project_inforamtion_and_context list for inclusion in the prompt.
		Usage: `result = await service.add_project_context_hook(payload)`
		"""
		state = payload.get("state", {})
		project_inforamtion_and_context = state.get("project_inforamtion_and_context", [])

		if self.conventions.is_not_empty():
			conventions = "\n\n".join(self.conventions.all().values())

			project_inforamtion_and_context.append(
				(
					"user",
					dedent(f"""
					# Coding and Project Conventions
					**Important:** Adhere to the following project-specific conventions. These standards are essential for maintaining code quality and consistency.
					{conventions}
					"""),
				)
			)

		state["project_inforamtion_and_context"] = project_inforamtion_and_context

		return payload.set("state", state)
