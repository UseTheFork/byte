"""Configuration settings for ByteSmith."""

import os


class Settings:
    """Application settings."""

    def __init__(self):
        self.debug = os.getenv("BYTESMITH_DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("BYTESMITH_LOG_LEVEL", "INFO")

        # LangChain/OpenAI settings (for future use)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.langchain_api_key = os.getenv("LANGCHAIN_API_KEY")

    @property
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.openai_api_key)


# Global settings instance
settings = Settings()
