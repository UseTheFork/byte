from byte.support import ArrayStore


class Configurable:
    """Mixin that provides configuration storage capabilities.

    Enables classes to store and retrieve configuration settings through
    a flexible ArrayStore instance accessible via the config() method.
    Usage: `class MyService(Configurable): self.config().add("key", "value")`
    """

    _config: ArrayStore = ArrayStore()

    def config(self) -> ArrayStore:
        """Get the configuration store for this instance.

        Returns the ArrayStore instance for managing configuration settings.
        Usage: `self.config().add("timeout", 30).add("retries", 3)`
        """
        return self._config

    def boot_configurable(self, **kwargs):
        """Boot the configurable mixin.

        Called automatically during the boot phase to initialize configuration
        storage. Override in subclasses if configuration setup is needed.

        Usage: Called automatically via _boot_mixins() during service initialization
        """
        pass
