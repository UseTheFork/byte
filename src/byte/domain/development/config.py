from pydantic import BaseModel, Field


class DevelopmentConfig(BaseModel):
	"""Development domain configuration for internal debugging and testing features.

	This configuration is excluded from serialization and can be enabled via
	the BYTE_DEV_MODE environment variable for development purposes.
	"""

	enable: bool = Field(default=False, description="Enable or disable development mode features")
