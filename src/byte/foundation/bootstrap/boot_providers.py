from __future__ import annotations

from typing import TYPE_CHECKING

from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


class BootProviders(Bootstrapper):
    def bootstrap(self, app: Application) -> None:
        app.boot()
