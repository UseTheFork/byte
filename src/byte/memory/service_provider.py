from byte import ServiceProvider
from byte.memory import (
    ClearCommand,
    MemoryService,
    ResetCommand,
)


class MemoryServiceProvider(ServiceProvider):
    """Service provider for conversation memory management.

    Registers memory services for short-term conversation persistence using
    LangGraph checkpointers. Enables stateful conversations and thread
    management for the AI agent system.
    Usage: Register with container to enable conversation memory
    """

    def services(self):
        return [
            # keep-sorted start
            MemoryService,
            # keep-sorted end
        ]

    def commands(self):
        return [
            # keep-sorted start
            ClearCommand,
            ResetCommand,
            # keep-sorted end
        ]
