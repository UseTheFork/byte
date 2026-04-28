from dataclasses import dataclass, field

from byte.event import Event


class SystemEvents:
    """Namespace for all system based event types."""

    @dataclass
    class PostBoot(Event):
        """Event emitted after application boot to gather initialization info."""

        messages: list[str] = field(default_factory=list)
