from __future__ import annotations

from typing import TYPE_CHECKING

from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


class RegisterProviders(Bootstrapper):
    _merge: list[type] = []

    @staticmethod
    def merge(providers: list[type]) -> None:
        """
        Merge the given providers into the provider configuration before registration.

        Args:
            providers: List of provider classes to merge.
            bootstrap_provider_path: Optional path to bootstrap providers file.
        """
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for provider in providers:
            if provider is not None and provider not in seen:
                seen.add(provider)
                unique.append(provider)
        RegisterProviders._merge = unique

    def bootstrap(self, app: Application) -> None:
        """
        Register all service providers with the application.

        Args:
            app: The application instance.
        """
        # Get providers from application configuration
        providers = RegisterProviders._merge

        # Register each provider
        for provider_class in providers:
            app.register(provider_class)
