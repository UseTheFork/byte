import click

from byte.main import main


@click.command()
def cli():
    """Byte CLI Assistant"""
    main()


if __name__ == "__main__":
    cli()
