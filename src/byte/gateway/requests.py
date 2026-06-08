from dataclasses import dataclass


@dataclass
class GatewayRequest:
    """Base class for typed gateway requests."""

    id: str | int


class Requests:
    """Namespace for typed gateway request classes."""

    @dataclass
    class Configure(GatewayRequest):
        """Configure gateway parameters."""

        model: str | None = None
        context_limit: int | None = None

    @dataclass
    class AddFile(GatewayRequest):
        """Add file to AI context as editable."""

        file_path: str

    @dataclass
    class DropFile(GatewayRequest):
        """Remove file from AI context."""

        file_path: str

    @dataclass
    class ContextAddFile(GatewayRequest):
        """Add file contents to session context."""

        file_path: str
