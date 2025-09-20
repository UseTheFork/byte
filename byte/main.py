import asyncio

from rich.console import Console

from byte.bootstrap import bootstrap, shutdown
from byte.container import Container
from byte.context import container_context
from byte.core.cli import cli
from byte.core.config.config import ByteConfg


class Byte:
    """Main application class that orchestrates the CLI interface and command processing.

    Separates concerns by delegating prompt handling to PromptHandler and command
    processing to CommandProcessor, while maintaining the main event loop.
    """

    def __init__(self, container: Container):
        self.container = container
        self.actor_tasks = []

    async def initialize(self):
        """Discover and start all registered actors"""
        # Get all registered actor instances
        # Since ServiceProviders have already registered them as singletons
        actors = await self._discover_actors()

        # Start all actors
        for actor in actors:
            task = asyncio.create_task(actor.start())
            task.set_name(f"actor_{actor.name}")
            self.actor_tasks.append(task)

        return self.actor_tasks

    async def _discover_actors(self):
        """Discover all registered actor instances from the container"""
        actors = []

        # Get all service providers that have actors
        if hasattr(self.container, "_service_providers"):
            for provider in self.container._service_providers:
                if hasattr(provider, "provides_actors"):
                    for actor_class in provider.provides_actors():
                        actor = await self.container.make(actor_class)
                        actors.append(actor)

        return actors

    async def run(self):
        """Run the actor-based application"""
        try:
            tasks = await self.initialize()

            if not tasks:
                print("No actors registered!")
                return

            # Wait for any task to complete (likely shutdown)
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()

            # Wait for all tasks to finish
            await asyncio.gather(*pending, return_exceptions=True)

        except KeyboardInterrupt:
            print("\nShutting down...")
            await self._shutdown()

    async def _shutdown(self):
        """Graceful shutdown of all actors"""
        # Cancel all tasks
        for task in self.actor_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.actor_tasks, return_exceptions=True)


async def main(config: ByteConfg):
    """Simplified application entry point using actor system."""
    container = await bootstrap(config)
    container_context.set(container)

    # Create and run the actor-based app
    app = Byte(container)
    await app.run()

    # Cleanup
    await shutdown(container)

    console = Console()
    console.print("[warning]Goodbye![/warning]")


def run(config: ByteConfg):
    asyncio.run(main(config))


if __name__ == "__main__":
    cli()
