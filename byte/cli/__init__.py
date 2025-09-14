import click

from byte.main import cli as main_cli


@click.command()
def cli():
    """Byte CLI Assistant"""
    main_cli()


if __name__ == "__main__":
    cli()
