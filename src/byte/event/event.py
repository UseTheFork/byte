from __future__ import annotations

from typing import TYPE_CHECKING

from byte.support import Str

if TYPE_CHECKING:
    pass


class Event:
    """Base class for all events with optional metadata."""

    __slots__ = [
        "_stop_propagation",
        "time",
    ]

    def __post_init__(self) -> None:
        """Allow dataclasses to initialize the object."""
        # self.time: float = _time.get_time()
        self._stop_propagation = False

    def __init__(self) -> None:
        self.__post_init__()

    def __init_subclass__(
        cls,
    ) -> None:
        super().__init_subclass__()
        # a class defined inside of a function will have a qualified name like func.<locals>.Class,
        # so make sure we only use the actual class name(s)
        qualname = cls.__qualname__.rsplit("<locals>.", 1)[-1]
        # only keep the last two parts of the qualified name of deeply nested classes
        # for backwards compatibility, e.g. A.B.C.D becomes C.D
        namespace = qualname.rsplit(".", 2)[-2:]
        name = "_".join(Str.snake_case(part) for part in namespace)
        cls.handler_name = f"on_{name}"
