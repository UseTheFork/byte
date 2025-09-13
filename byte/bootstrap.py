from byte.container import app
from byte.core.command.registry import command_registry
from byte.core.events.service_provider import EventServiceProvider
from byte.domain.commit.service_provider import CommitServiceProvider
from byte.domain.files.file_service_provider import FileServiceProvider
from byte.domain.llm.service_provider import LLMServiceProvider
from byte.domain.system.service_provider import SystemServiceProvider
from byte.domain.ui.service_provider import UIServiceProvider


def bootstrap():
    # Bind command registry to container
    app.singleton("command_registry", lambda: command_registry)

    # Define all service providers
    service_providers = [
        EventServiceProvider(),  # Register events first
        UIServiceProvider(),
        FileServiceProvider(),
        LLMServiceProvider(),
        CommitServiceProvider(),
        SystemServiceProvider(),
    ]

    # Register all service providers
    for provider in service_providers:
        provider.register(app)

    # Boot all service providers
    for provider in service_providers:
        provider.boot(app)

    return app
