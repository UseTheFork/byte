"""Configuration settings for Byte."""

import os


class Settings:
    """Application settings."""

    def __init__(self):
        self.debug = os.getenv("BYTE_DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("BYTE_LOG_LEVEL", "INFO")

        # LLM Provider settings
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
        self.preferred_llm_provider = os.getenv("BYTE_LLM_PROVIDER")

    @property
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.openai_api_key)
    
    @property
    def has_anthropic_key(self) -> bool:
        """Check if Anthropic API key is configured."""
        return bool(self.anthropic_api_key)
    
    @property
    def has_google_key(self) -> bool:
        """Check if Google API key is configured."""
        return bool(self.google_api_key)


# Global settings instance
settings = Settings()
