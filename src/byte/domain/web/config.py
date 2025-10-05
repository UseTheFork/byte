from pathlib import Path

from pydantic import BaseModel, Field


class WebConfig(BaseModel):
    """"""

    chrome_binary_location: Path = Field(default=Path("/usr/bin/google-chrome"))
