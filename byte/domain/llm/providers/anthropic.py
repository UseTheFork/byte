import os

from langchain_anthropic import ChatAnthropic

from byte.domain.llm.service import LLMService


class AnthropicLLMService(LLMService):
    def get_model_config(self) -> dict:
        return {
            "main": {
                "model": "claude-3-5-sonnet-20241022",
                "thinking": {"type": "enabled", "budget_tokens": 2000},
            },
            "weak": {
                "model": "claude-3-5-haiku-20241022",
            },
        }

    def _create_model(self, model_name: str, **kwargs):
        return ChatAnthropic(model=model_name, **kwargs)

    def is_available(self) -> bool:
        return bool(os.getenv("ANTHROPIC_API_KEY"))
