from pathlib import Path

from pydantic import BaseModel, Field


class WebConfig(BaseModel):
    """Configuration for web browser automation and scraping.

    Defines settings for headless Chrome browser operations including
    binary location and browser behavior customization.
    """

    enable: bool = Field(default=False, description="Enable web commands", exclude=True)

    chrome_binary_location: Path | None = Field(
        description="Path to Chrome/Chromium binary executable for headless browser automation", default=None
    )
