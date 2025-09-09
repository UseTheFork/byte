import click

from bytesmith.main import main


@click.command()
def cli():
    """ByteSmith CLI Assistant"""
    main()


if __name__ == "__main__":
    cli()
