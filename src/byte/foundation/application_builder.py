from __future__ import annotations

from typing import TYPE_CHECKING

from byte.foundation import Kernel

if TYPE_CHECKING:
    from byte.foundation import Application


class ApplicationBuilder:
    def __init__(self, application: Application):
        """Create a new application builder instance."""
        self._application = application

    def with_kernels(self) -> ApplicationBuilder:
        """
        Register the console kernel as a singleton.

        Returns:
            ApplicationBuilder instance for chaining.
        """
        self._application.singleton(Kernel)

        return self

    def with_providers(
        self, providers: list[type] | None = None, with_bootstrap_providers: bool = True
    ) -> ApplicationBuilder:
        """
        Register service providers with the application.

        Args:
            providers: List of provider classes to register.
            with_bootstrap_providers: Whether to include bootstrap providers.

        Returns:
            ApplicationBuilder instance for chaining.
        """

        if providers is None:
            providers = []

        return self

    def create(self) -> Application:
        """
        Get the application instance.

        Returns:
            Application instance.
        """

        return self._application
