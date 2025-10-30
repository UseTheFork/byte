import os
from importlib.metadata import PackageNotFoundError, version

import yaml

from byte.core.config.config import BYTE_CONFIG_FILE, ByteConfg


class ConfigLoaderService:
	"""Load and parse configuration from YAML file.

	Loads the BYTE_CONFIG_FILE and returns a dictionary that can be
	passed to ByteConfig for initialization.
	Usage: `loader = ConfigLoaderService()`
	Usage: `config_dict = loader()` -> {"llm": {...}, "files": {...}}
	"""

	def _load_yaml_config(self) -> dict:
		"""Load and parse YAML configuration file.

		Returns a dictionary of configuration values from YAML file.
		Usage: `config_dict = self._load_yaml_config()`
		"""
		with open(BYTE_CONFIG_FILE) as f:
			config = yaml.safe_load(f)

		return config if config is not None else {}

	def _apply_system_config(self, config: ByteConfg) -> ByteConfg:
		"""Apply system-level configuration settings.

		Usage: `config = self._apply_system_config(config)`
		"""

		try:
			config.system.version = version("byte-ai-cli")
		except PackageNotFoundError:
			pass

		return config

	def _apply_environment_overrides(self, config: ByteConfg) -> ByteConfg:
		"""Apply environment variable overrides to configuration.

		Checks for BYTE_DEV_MODE environment variable and enables development mode if set.
		Usage: `config = self._apply_environment_overrides(config)`
		"""
		# Enable development mode if BYTE_DEV_MODE environment variable is set
		if os.getenv("BYTE_DEV_MODE", "").lower() in ("true", "1", "yes"):
			config.development.enable = True

		return config

	def _load_llm_api_keys(self, config: ByteConfg) -> ByteConfg:
		"""Load and configure LLM API keys from environment variables.

		Detects available API keys and enables corresponding LLM providers.
		Validates that at least one provider is configured.
		Usage: `config = self._load_llm_api_keys(config)`
		"""
		# Auto-detect and configure Anthropic
		anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
		if anthropic_key:
			config.llm.anthropic.enable = True
			config.llm.anthropic.api_key = anthropic_key

		# Auto-detect and configure Anthropic
		gemini_key = os.getenv("GEMINI_API_KEY", "")
		if gemini_key:
			config.llm.gemini.enable = True
			config.llm.gemini.api_key = gemini_key

		# Auto-detect and configure OpenAI
		openai_key = os.getenv("OPENAI_API_KEY", "")
		if openai_key:
			config.llm.openai.enable = True
			config.llm.openai.api_key = openai_key

		# Validate that at least one provider is configured
		if not (config.llm.anthropic.enable or config.llm.gemini.enable or config.llm.openai.enable):
			raise ValueError(
				"Missing required API key. Please set at least one of: "
				"ANTHROPIC_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY environment variable."
			)

		return config

	def __call__(self) -> ByteConfg:
		"""Load configuration from BYTE_CONFIG_FILE.

		Returns a dictionary of configuration values parsed from YAML.
		Usage: `config_dict = loader()`
		"""

		yaml_config = self._load_yaml_config()

		config = ByteConfg(**yaml_config)
		config = self._apply_system_config(config)
		config = self._apply_environment_overrides(config)
		config = self._load_llm_api_keys(config)

		return config
