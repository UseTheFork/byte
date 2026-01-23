class ByteException(Exception):
    """Base exception for all Byte operations.

    All custom exceptions in the Byte project should inherit from this class.
    This provides a common base for catching any Byte-specific errors.
    Usage: `except ByteException as e: ...`
    """

    pass


class ByteConfigException(ByteException):
    """Base exception for configuration-related errors.

    Raised when configuration validation fails or required settings are missing.
    Usage: `except ByteConfigException as e: ...`
    """

    pass
