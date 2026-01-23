from __future__ import annotations

from typing import TYPE_CHECKING

from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


class SetContext(Bootstrapper):
    """"""

    def bootstrap(self, app: Application) -> None:
        """
        Bootstrap environment variable loading.

        Args:
            app: The application instance.
        """
        from byte.context import application_context

        application_context.set(app)
