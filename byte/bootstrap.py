from byte.container import app
from byte.core.command.registry import command_registry
from byte.domain.files.file_service_provider import FileServiceProvider
from byte.domain.system.service_provider import SystemServiceProvider


def bootstrap():
    # Bind command registry to container
    app.singleton("command_registry", lambda: command_registry)

    # Define all service providers
    service_providers = [
        FileServiceProvider(),
        SystemServiceProvider(),
    ]

    # Register all service providers
    for provider in service_providers:
        provider.register(app)

    # Boot all service providers
    for provider in service_providers:
        provider.boot(app)

    return app
