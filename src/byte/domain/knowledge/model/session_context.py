from typing import Literal

from pydantic import BaseModel, Field


class SessionContextModel(BaseModel):
	"""Model representing a session context item.

	Stores a key-value pair where the key identifies the context item
	and the content contains the actual context data to be used by the AI.
	"""

	type: Literal["web", "file", "agent"] = Field(description="Type identifier for the context item")
	key: str = Field(description="Unique identifier for the context item")
	content: str = Field(description="The actual context content/data")
