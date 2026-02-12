from byte.foundation import ByteException


class ParseError(ByteException):
    """Raised when SKILL.md parsing fails due to invalid format or missing content."""

    pass


class ValidationError(ByteException):
    """Raised when skill metadata fails validation rules."""

    pass
