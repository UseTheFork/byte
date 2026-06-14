from typing import List

from pydantic import BaseModel, Field


class DocumentationConfig(BaseModel):
    """Configure documentation framework, features, and writing style."""

    enable_mermaid: bool = Field(
        default=True,
        description="Use Mermaid for diagrams and charts",
    )
    framework: str = Field(
        default="mkdocs",
        description="Documentation framework (e.g. mkdocs, vitepress, docusaurus, sphinx)",
    )
    extra_guidelines: List[str] = Field(
        default_factory=list,
        description="Additional documentation guidelines",
    )
    style: str = Field(
        default="diataxis",
        description="Documentation writing style (e.g. diataxis, google, microsoft, minimal)",
    )
