import os

from langchain_openai import ChatOpenAI

from byte.domain.llm.service import LLMService


class OpenAILLMService(LLMService):
    def get_model_config(self) -> dict:
        return {
            "main": {
                "model": "gpt-4o",
                "temperature": 0,
                "max_tokens": None,
                "timeout": None,
                "max_retries": 2,
            },
            "weak": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_tokens": 2000,
                "max_retries": 2,
            },
        }

    def _create_model(self, model_name: str, **kwargs):
        return ChatOpenAI(model=model_name, **kwargs)

    def is_available(self) -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))
