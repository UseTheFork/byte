import click
from dotenv import load_dotenv
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.traceback import install

from byte.core.config.config import DOTENV_PATH, CLIArgs
from byte.domain.system.service.config_loader_service import ConfigLoaderService
from byte.domain.system.service.first_boot_service import FirstBootService


@click.command()
@click.option(
    "--read-only",
    multiple=True,
    help="Add files to read-only context (can be specified multiple times)",
)
@click.option(
    "--add",
    multiple=True,
    help="Add files to editable context (can be specified multiple times)",
)
def cli(read_only: tuple[str, ...], add: tuple[str, ...]):
    """Byte CLI Assistant"""
    from byte.main import run

    found_dotenv = load_dotenv(DOTENV_PATH, override=True)

    # Set rich as the default traceback handler early
    install(show_locals=True)

    # Check for first boot before bootstrapping
    initializer = FirstBootService()
    if initializer.is_first_boot():
        initializer.run_if_needed()

    try:
        cli_args = CLIArgs(
            read_only_files=list(read_only),
            editable_files=list(add),
        )
        loader = ConfigLoaderService(cli_args)
        config = loader()
        config.dotenv_loaded = found_dotenv

        run(config)
    except ValidationError as e:
        console = Console()

        error_messages = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_messages.append(f"[bold]{field}[/bold]: {message}")

        console.print(
            Panel(
                "\n".join(error_messages),
                title="Configuration Error",
                title_align="left",
                border_style="red",
            )
        )
        raise click.Abort


if __name__ == "__main__":
    cli()
