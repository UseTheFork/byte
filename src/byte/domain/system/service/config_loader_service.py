from typing import Any, Dict

import yaml

from byte.core.config.config import BYTE_CONFIG_FILE


class ConfigLoaderService:
	"""Load and parse configuration from YAML file.

	Loads the BYTE_CONFIG_FILE and returns a dictionary that can be
	passed to ByteConfig for initialization.
	Usage: `loader = ConfigLoaderService()`
	Usage: `config_dict = loader()` -> {"llm": {...}, "files": {...}}
	"""

	def __init__(self):
		pass

	def __call__(self) -> Dict[str, Any]:
		"""Load configuration from BYTE_CONFIG_FILE.

		Returns a dictionary of configuration values parsed from YAML.
		Usage: `config_dict = loader()`
		"""
		if not BYTE_CONFIG_FILE.exists():
			return {}

		with open(BYTE_CONFIG_FILE) as f:
			config = yaml.safe_load(f)

		return config if config is not None else {}
