from __future__ import annotations

from byte import ServiceProvider
from byte.logging import LogService


class LogServiceProvider(ServiceProvider):
    """ """

    def register(self) -> None:
        """ """
        self.app.singleton(LogService)

        self.app.instance("log", self.app.log())
