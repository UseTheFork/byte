from typing import TYPE_CHECKING

from byte.foundation.bootstrap.bootstrapper import Bootstrapper

if TYPE_CHECKING:
    from byte.foundation import Application


class RegisterProviders(Bootstrapper):
    """Register all service providers with the application."""

    _merge: list[type] = []

    @staticmethod
    def merge(providers: list[type]) -> None:
        """Merge provider classes into the provider configuration before registration."""
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for provider in providers:
            if provider is not None and provider not in seen:
                seen.add(provider)
                unique.append(provider)
        RegisterProviders._merge = unique

    def bootstrap(self, app: Application) -> None:
        """Register all service providers with the application."""
        # Get providers from application configuration
        providers = RegisterProviders._merge

        # Register each provider
        for provider_class in providers:
            app.register(provider_class)
