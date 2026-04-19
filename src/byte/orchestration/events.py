from dataclasses import dataclass, field

from byte.event import Event


class OrchestrationEvents:
    """Namespace for all orchestration based event types."""

    @dataclass
    class GatherReinforcement(Event):
        # TODO: Doc String here.
        """"""

        agent: str
        model: str
        provider: str
        reinforcement: list[str] = field(default_factory=list)
        session_docs: list[str] = field(default_factory=list)
        system_context: list[str] = field(default_factory=list)

    @dataclass
    class GatherProjectContext(Event):
        # TODO: Doc String here.
        """"""

        conventions: list[str] = field(default_factory=list)
        session_docs: list[str] = field(default_factory=list)
        system_context: list[str] = field(default_factory=list)
