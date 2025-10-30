import click
from dotenv import load_dotenv

from byte.core.config.config import DOTENV_PATH
from byte.domain.system.service.config_loader_service import ConfigLoaderService
from byte.domain.system.service.first_boot_service import FirstBootService


@click.command()
def cli():
	"""Byte CLI Assistant"""
	from byte.main import run

	found_dotenv = load_dotenv(DOTENV_PATH, override=True)

	# Check for first boot before bootstrapping
	initializer = FirstBootService()
	if initializer.is_first_boot():
		initializer.run_if_needed()

	loader = ConfigLoaderService()
	config = loader()
	config.dotenv_loaded = found_dotenv

	run(config)


if __name__ == "__main__":
	cli()
