from byte.foundation import ByteException


class ByteAgentException(ByteException):
    """ """

    pass


class DummyNodeReachedException(ByteAgentException):
    """Exception raised when execution reaches a dummy node.

    Dummy nodes are placeholders that should never be reached during normal
    graph execution. If this exception is raised, it indicates a routing error
    in the agent graph where an edge points to an unimplemented node.

    Usage: `raise DummyNodeReachedException("Reached unimplemented node: tool_node")`
    """

    pass
