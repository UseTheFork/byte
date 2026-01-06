from byte.foundation import ByteException


class ByteConfigException(ByteException):
    """Base exception for configuration-related errors.

    Raised when configuration validation fails or required settings are missing.
    Usage: `except ByteConfigException as e: ...`
    """

    pass
