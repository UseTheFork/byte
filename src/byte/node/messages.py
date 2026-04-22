from datetime import datetime

from langchain.messages import AIMessage as LangchainAIMessage
from pydantic import Field


class BaseAIMessage(LangchainAIMessage):
    created_at: datetime = Field(default_factory=datetime.now)


class ByteAIMessage:
    class CoderPlanAgentMessage(BaseAIMessage):
        pass

    class CoderAgentMessage(BaseAIMessage):
        pass

    class AskAgentMessage(BaseAIMessage):
        pass

    class CommitAgentMessage(BaseAIMessage):
        pass
