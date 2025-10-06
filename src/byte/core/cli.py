import click
from dotenv import load_dotenv

from byte.core.config.config import ByteConfg
from byte.core.initializer import FirstBootInitializer


@click.command()
def cli():
    """Byte CLI Assistant"""
    load_dotenv()

    from byte.main import run

    # Check for first boot before bootstrapping
    initializer = FirstBootInitializer()
    if initializer.is_first_boot():
        initializer.run_if_needed()

    config = ByteConfg()  # pyright: ignore[reportCallIssue]
    run(config)


if __name__ == "__main__":
    cli()
