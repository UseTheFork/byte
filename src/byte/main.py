import asyncio
import sys
from pathlib import Path

from pydantic import ValidationError

from byte.cli import CLIServiceProvider
from byte.context import application_context
from byte.foundation import Application
from byte.knowledge import KnowledgeServiceProvider
from byte.memory import MemoryServiceProvider
from byte.system import SystemServiceProvider


def cli():
    """Byte CLI Assistant"""

    try:
        providers = [
            CLIServiceProvider,
            MemoryServiceProvider,
            KnowledgeServiceProvider,
            SystemServiceProvider,
        ]
        application = Application.configure(Path.cwd(), providers).create()
        application_context.set(application)

    except ValidationError:
        raise

    asyncio.run(application.handle_command(sys.argv))


if __name__ == "__main__":
    cli()


# from byte.core.cli import cli

# class Byte:
#     """Main application class that orchestrates the CLI interface and command processing.

#     Separates concerns by delegating prompt handling to PromptHandler and command
#     processing to CommandProcessor, while maintaining the main event loop.
#     """

#     def __init__(self, container: Container):
#         self.container = container
#         self.actor_tasks = []

#     async def initialize(self):
#         """Discover and start all registered actors"""

#         # Store the TaskManager for shutdown later.
#         self.task_manager = await self.container.make(TaskManager)

#         # Do boot config operations based on CLI invocation
#         config = await self.container.make(ByteConfig)
#         file_service = await self.container.make(FileService)

#         # Add read-only files from boot config
#         if config.boot.read_only_files:
#             for file_path in config.boot.read_only_files:
#                 await file_service.add_file(file_path, FileMode.READ_ONLY)

#         # Add editable files from boot config
#         if config.boot.editable_files:
#             for file_path in config.boot.editable_files:
#                 await file_service.add_file(file_path, FileMode.EDITABLE)

#     async def _main_loop(self):
#         """Main application loop - easy to follow"""
#         input_service = await self.container.make(PromptToolkitService)

#         while True:
#             try:
#                 # Get user input (this can be async/non-blocking)
#                 await input_service.execute()
#             except KeyboardInterrupt:
#                 break
#             except Exception as e:
#                 log.exception(e)
#                 console = await self.container.make(ConsoleService)
#                 console.print_error_panel(
#                     str(e),
#                     title="Exception",
#                 )

#     async def run(self):
#         """Run the main application loop.

#         Initializes the application, starts the main loop, and ensures proper cleanup
#         of the task manager on exit.
#         """
#         await self.initialize()
#         try:
#             await self._main_loop()
#         finally:
#             await self.task_manager.shutdown()
#             # console.console.print_exception(show_locals=True)


# async def main(config: ByteConfig):
#     """Application entry point"""
#     container = await bootstrap(config)
#     container_context.set(container)

#     # Create and run the actor-based app
#     app = Byte(container)
#     await app.run()

#     # Cleanup
#     await shutdown(container)

#     console = Console()
#     console.print("[warning]Goodbye![/warning]")


# def run(config: ByteConfig):
#     asyncio.run(main(config))
