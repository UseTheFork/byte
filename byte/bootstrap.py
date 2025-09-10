from byte.container import app
from byte.commands.registry import command_registry
from byte.domain.files.file_service_provider import FileServiceProvider


def bootstrap():
    # Bind command registry to container
    app.singleton("command_registry", lambda: command_registry)
    
    # Register service providers
    file_provider = FileServiceProvider()
    file_provider.register(app)
    file_provider.boot(app)

    # Boot services
    return app
