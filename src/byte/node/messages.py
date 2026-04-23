from datetime import datetime

from langchain.messages import AIMessage as LangchainAIMessage
from pydantic import Field


class BaseAIMessage(LangchainAIMessage):
    agent_name: str = Field(default="")
    mask: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)


class ByteAIMessage:
    class CoderPlanAgentMessage(BaseAIMessage):
        agent_name: str = "Coder Plan Agent"

    class CoderAgentMessage(BaseAIMessage):
        agent_name: str = "Coder Agent"

    class AskAgentMessage(BaseAIMessage):
        agent_name: str = "Ask Agent"

    class CommitAgentMessage(BaseAIMessage):
        agent_name: str = "Commit Agent"
        mask: bool = True
