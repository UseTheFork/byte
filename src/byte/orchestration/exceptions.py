from byte.foundation import ByteException


class ByteAgentException(ByteException):
    """Raise when a byte agent operation fails."""

    pass


class PhaseException(ByteAgentException):
    """Raise when a phase operation fails."""

    pass


class DummyNodeReachedException(ByteAgentException):
    """Raise when execution reaches an unimplemented dummy node."""

    pass
