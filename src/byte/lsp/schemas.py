from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LspServerState(Enum):
    """LSP server connection states."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    FAILED = "failed"


class Position(BaseModel):
    """Position in a text document."""

    line: int = Field(description="Line position in a document (zero-based)")
    character: int = Field(description="Character offset on a line (zero-based)")


class Range(BaseModel):
    """Range in a text document."""

    start: Position
    end: Position


class Location(BaseModel):
    """Location in a text document."""

    uri: str = Field(description="Document URI")
    range: Range


class TextDocumentIdentifier(BaseModel):
    """Identifies a text document."""

    uri: str = Field(description="Document URI")


class HoverResult(BaseModel):
    """Result from a hover request."""

    contents: str = Field(description="Hover content as markdown or plain text")
    range: Optional[Range] = Field(default=None, description="Optional range for the hover")


class CompletionItem(BaseModel):
    """A completion item."""

    label: str = Field(description="The label of this completion item")
    kind: Optional[int] = Field(default=None, description="The kind of this completion item")
    detail: Optional[str] = Field(default=None, description="A human-readable string with additional information")
    documentation: Optional[str] = Field(default=None, description="Documentation for this completion item")


class DiagnosticSeverity(Enum):
    """Diagnostic severity levels."""

    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4


class Diagnostic(BaseModel):
    """Represents a diagnostic, such as a compiler error or warning."""

    range: Range = Field(description="The range at which the diagnostic applies")
    severity: Optional[int] = Field(default=None, description="The diagnostic's severity")
    code: Optional[str] = Field(default=None, description="The diagnostic's code")
    source: Optional[str] = Field(default=None, description="A human-readable string describing the source")
    message: str = Field(description="The diagnostic's message")
