from __future__ import annotations

import shutil
import sys
from typing import TYPE_CHECKING

from byte import dd
from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


class PrepareEnvironment(Bootstrapper):
    """"""

    def _prepare_directories(self, app: Application):
        """Check if this is the first time Byte is being run.

        Usage: `if await initializer.is_first_boot(): ...`
        """

        session_context_path = app.session_context_path()

        # Delete and recreate session_context to ensure it's empty on each boot
        if session_context_path.exists():
            shutil.rmtree(session_context_path)
        session_context_path.mkdir(exist_ok=True)

        app.cache_path().mkdir(exist_ok=True)
        app.conventions_path().mkdir(exist_ok=True)

    def bootstrap(self, app: Application) -> None:
        """ """

        self._prepare_directories(app)

        # TODO: complete first boot service
        if not self.is_first_boot(app):
            return

        # config = app.instance("console", ByteConfig(**yaml_config))

        # console = app.make(Console)

        dd(sys.argv)

    def is_first_boot(self, app: Application) -> bool:
        """Check if this is the first time Byte is being run.

        Usage: `if await initializer.is_first_boot(): ...`
        """

        return not app.config_path().exists()
