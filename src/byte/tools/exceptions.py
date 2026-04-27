from byte.foundation.exceptions import ByteException


class ToolException(ByteException):
    """Base exception for all tool-related errors."""

    pass


class ToolNotFoundException(ToolException):
    """Raised when a requested tool is not found in the registry."""

    def __init__(self, message: str = "", tool_call: dict | None = None):
        self.tool_call = tool_call
        super().__init__(message)


class ToolValidationException(ToolException):
    """Raised when a tool's input fails validation."""

    pass


class ToolRunException(ByteException):
    """Raised when an error occurs during tool execution."""

    pass
