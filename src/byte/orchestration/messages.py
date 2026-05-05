from datetime import datetime

from langchain.messages import AIMessage as LangchainAIMessage
from pydantic import Field


class AIMessage(LangchainAIMessage):
    agent_name: str = Field(default="")
    mask: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_langchain(cls, message: LangchainAIMessage, **kwargs) -> AIMessage:
        """Convert a LangChain AIMessage to our custom AIMessage."""
        return cls(
            content=message.content,
            additional_kwargs=message.additional_kwargs,
            response_metadata=message.response_metadata,
            tool_calls=message.tool_calls,
            invalid_tool_calls=message.invalid_tool_calls,
            usage_metadata=message.usage_metadata,
            id=message.id,
            **kwargs,
        )
