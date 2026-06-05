from typing import TYPE_CHECKING

from byte.foundation import Kernel
from byte.foundation.bootstrap import RegisterProviders

if TYPE_CHECKING:
    from byte.foundation import Application


class ApplicationBuilder:
    def __init__(self, application: Application):
        """Create a new application builder instance."""
        self._application = application

    def with_kernels(self) -> ApplicationBuilder:
        """Register the console kernel as a singleton."""
        self._application.singleton(Kernel)

        return self

    def with_providers(self, providers: list[type] | None = None) -> ApplicationBuilder:
        """Register service providers with the application."""

        if providers is None:
            providers = []

        RegisterProviders.merge(providers)

        return self

    def create(self) -> Application:
        """Get the application instance."""

        return self._application
