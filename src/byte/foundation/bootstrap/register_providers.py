from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

from byte import Log
from byte.foundation.bootstrap.bootstrapper import Bootstrapper
from byte.support import ServiceProvider

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
        log = app.make(Log)

        # Register each provider
        for provider_class in providers:
            # Check that provider extends ServiceProvider
            if not (inspect.isclass(provider_class) and issubclass(provider_class, ServiceProvider)):
                raise TypeError(
                    f"Provider {provider_class.__name__ if inspect.isclass(provider_class) else provider_class} "
                    f"must extend ServiceProvider"
                )

            log.debug("Register Service Provider: {}", provider_class.__name__)
            app.singleton(provider_class)

            # Instantiate the provider
            provider = app.make(provider_class, app=app)

            # Call the register method if it exists
            if hasattr(provider, "register") and callable(provider.register):
                provider.register()

            # # Call the register services method if it exists
            if hasattr(provider, "register_services") and callable(provider.register_services):
                provider.register_services()

            # Call the register services method if it exists
            if hasattr(provider, "register_commands") and callable(provider.register_commands):
                provider.register_commands()
