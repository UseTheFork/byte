import os

from langchain_google_genai import ChatGoogleGenerativeAI

from byte.domain.llm.service import LLMService


class GeminiLLMService(LLMService):
    def get_model_config(self) -> dict:
        return {
            "main": {
                "model": "gemini-1.5-pro",
                "temperature": 0,
                "max_tokens": None,
                "max_retries": 2,
            },
            "weak": {
                "model": "gemini-1.5-flash",
                "temperature": 0.3,
                "max_tokens": 2000,
                "max_retries": 2,
            },
        }

    def _create_model(self, model_name: str, **kwargs):
        return ChatGoogleGenerativeAI(model=model_name, **kwargs)

    def is_available(self) -> bool:
        return bool(os.getenv("GOOGLE_API_KEY"))
