import click

from byte.core.config.config import ByteConfg


@click.command()
def cli():
    """Byte CLI Assistant"""
    from byte.main import run

    config = ByteConfg()  # pyright: ignore[reportCallIssue]
    run(config)


if __name__ == "__main__":
    cli()
