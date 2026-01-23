from __future__ import annotations

import os
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


class LoadEnvironmentVariables(Bootstrapper):
    """Bootstrap class for loading environment variables from .env file."""

    def _check_llm_api_keys(self):
        """"""
        # Auto-detect and configure Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        # Validate that at least one provider is configured
        if not (anthropic_key or gemini_key or openai_key):
            raise ValueError(
                "Missing required API key. Please set at least one of: "
                "ANTHROPIC_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY environment variable."
            )

    def bootstrap(self, app: Application) -> None:
        """
        Bootstrap environment variable loading.

        Args:
            app: The application instance.
        """
        env_file_path = app.environment_file_path()

        if env_file_path.exists():
            load_dotenv(dotenv_path=env_file_path)

        self._check_llm_api_keys()
