""""""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.event.event import Event
    from byte.event.event_bus import EventBus
    from byte.event.service_provider import EventsServiceProvider


__all__ = ("Event", "EventBus", "Events", "EventsServiceProvider")

_dynamic_imports = {
    # keep-sorted start
    "Event": "event",
    "EventBus": "event_bus",
    "Events": "event",
    "EventsServiceProvider": "service_provider",
    # keep-sorted end
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
