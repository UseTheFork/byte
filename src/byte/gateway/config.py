from pydantic import BaseModel, Field


class GatewayConfig(BaseModel):
    """Gateway domain configuration."""

    enable: bool = Field(default=False, description="Whether the gateway server starts at boot")
    host: str = Field(default="127.0.0.1", description="Hostname to bind the gateway server to")
    port: int = Field(
        default=0, description="Port to bind the gateway server to (0 lets the OS choose an available port)"
    )
