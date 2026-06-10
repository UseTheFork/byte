from pydantic import BaseModel, Field


class GatewayConfig(BaseModel):
    """Gateway domain configuration."""

    enable: bool = Field(default=False)
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=0)
