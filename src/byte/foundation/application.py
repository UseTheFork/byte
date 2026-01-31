import inspect
from pathlib import Path
from typing import Callable, Optional, TypeVar

from git import InvalidGitRepositoryError, Repo

from byte import ServiceProvider, TaskManager
from byte.foundation import Console, Container, FoundationServiceProvider, Kernel
from byte.foundation.bootstrap import RegisterProviders
from byte.logging import LogService, LogServiceProvider

T = TypeVar("T")


class Application(Container):
    """The main application container that manages service providers and application lifecycle.

    Usage: `app = Application.configure(base_path=Path.cwd())` -> creates configured application instance
    Usage: `await app.boot()` -> boots all registered service providers
    Usage: `await app.run()` -> starts interactive prompt session
    """

    def _register_base_bindings(self):
        """Register the basic bindings into the container."""
        self.instance("app", self)
        self.instance(Application, self)
        self.instance(Container, self)

    def _register_base_service_providers(self):
        """Register all of the base service providers."""

        self.register(LogServiceProvider)
        self.register(FoundationServiceProvider)

    def _register_base_service_provider_bindings(self):
        """Register base service provider instances in the container.

        Usage: Called internally during application initialization to bind log and console services.
        """
        self.instance("console", self.console())

        return self

    def __init__(self, base_path: Optional[Path] = None):
        super().__init__()
        self._has_been_bootstrapped = False
        self._booted = False
        self._booting_callbacks = []
        self._booted_callbacks = []

        if base_path:
            self.set_base_path(base_path)

        self._register_base_bindings()
        self._register_base_service_providers()
        self._register_base_service_provider_bindings()

    @staticmethod
    def configure(base_path: Optional[Path] = None, providers: list[type] | None = []):
        """
        Create and configure a new Application instance.

        Args:
            base_path: Optional base path for the application.

        Returns:
            Application instance.
        """
        from byte.foundation.application_builder import ApplicationBuilder

        return ApplicationBuilder(Application(base_path=base_path)).with_kernels().with_providers(providers)

    def _set_git_root_path(self) -> None:
        """Set the Git repository root path by traversing up from the start path.

        Usage: Called internally from `set_base_path` to find and store the Git repository root.
        """
        try:
            repo = Repo(self._base_path, search_parent_directories=True)
            self._git_root_path = Path(repo.working_dir)
        except InvalidGitRepositoryError:
            raise RuntimeError(f"No Git repository found starting from {self._base_path}")

    def set_base_path(self, base_path: Path):
        """Set the base paths."""
        self._base_path = base_path

        self._set_git_root_path()
        self.bind_paths_in_container()

        return self

    def bootstrap_with(self, bootstrappers: list) -> None:
        self._has_been_bootstrapped = True

        for bootstrapper in bootstrappers:
            instance = self.make(bootstrapper)
            instance.bootstrap(self)

    def booting(self, callback: Callable) -> None:
        """
        Register a new boot listener.

        Args:
            callback: Callback to execute during boot.

        Returns:
            None
        """
        self._booting_callbacks.append(callback)

    def booted(self, callback: Callable):
        """
        Register a new "booted" listener.

        Args:
            callback: Callable to execute when application is booted.

        Returns:
            None
        """
        self._booted_callbacks.append(callback)

        # TODO: need to figure out how to make this async friendly
        if self.is_booted():
            callback(self)

    def is_booted(self) -> bool:
        """
        Determine if the application has been booted.

        Returns:
            bool
        """
        return self._booted

    async def boot(self) -> None:
        """
        Boot the application's service providers.

        Returns:
            None
        """
        if self.is_booted():
            return

        # Fire booting callbacks
        for callback in self._booting_callbacks:
            callback(self)

        providers = RegisterProviders._merge
        for provider in providers:
            provider_instance = self.make(provider)
            await self.boot_provider(provider_instance)

        # Fire booted callbacks
        for callback in self._booted_callbacks:
            if inspect.iscoroutinefunction(callback):
                await callback(self)
            else:
                callback(self)

        self._booted = True

    async def boot_provider(self, provider: ServiceProvider) -> None:
        """
        Boot the application's service providers.

        Returns:
            None
        """
        if hasattr(provider, "boot") and callable(getattr(provider, "boot")):
            await provider.boot()

    def bind_paths_in_container(self):
        """Set the base paths."""
        self.instance("path", self.root_path())
        self.instance("path.app", self.app_path())
        self.instance("path.root", self.root_path())
        self.instance("path.config", self.config_path())
        self.instance("path.cache", self.cache_path())
        self.instance("path.conventions", self.conventions_path())
        self.instance("path.session_context", self.session_context_path())

        return self

    def log(self) -> LogService:
        """Get the Log service instance from the container.

        Usage: `app.log()` -> returns Log instance for logging operations
        """
        return self.make(LogService)

    def console(self) -> Console:
        """Get the Console service instance from the container.

        Usage: `app.console()` -> returns Console instance for terminal output
        """
        return self.make(Console)

    def path(self, path: str = "") -> Path:
        """
        Get the path to the "root" directory.

        Args:
            path: Optional path to append to the root directory.

        Returns:
            The full path to the root directory or subdirectory.
        """
        return self.join_paths(self.root_path(), path)

    def app_path(self, path: str = "") -> Path:
        """
        Get the path to the Byte application installation.

        Args:
            path: Optional path to append to the app path.

        Returns:
            The full path to the Byte installation directory or subdirectory.
        """
        byte_package_path = Path(__file__).parent.parent
        return self.join_paths(byte_package_path, path)

    def base_path(self, path: str = "") -> Path:
        """
        Get the base path of the application installation.

        Args:
            path: Optional path to append to the base path.

        Returns:
            The full base path or base path with appended subdirectory.
        """
        return self.join_paths(self._base_path, path)

    def root_path(self, path: str = "") -> Path:
        """
        Get the root path of the Git repository.

        Args:
            path: Optional path to append to the root path.

        Returns:
            The full root path or root path with appended subdirectory.
        """
        return self.join_paths(self._git_root_path, path)

    def config_path(self, path: str = "") -> Path:
        """
        Get the path to the application configuration directory.

        Args:
            path: Optional path to append to the config directory.

        Returns:
            The full path to the config directory or subdirectory.
        """
        base = self.root_path(".byte")
        return self.join_paths(base, path)

    def cache_path(self, path: str = "") -> Path:
        """
        Get the path to the application cache directory.

        Args:
            path: Optional path to append to the cache directory.

        Returns:
            The full path to the cache directory or subdirectory.
        """
        base = self.config_path("cache")
        return self.join_paths(base, path)

    def conventions_path(self, path: str = "") -> Path:
        """
        Get the path to the conventions directory.

        Args:
            path: Optional path to append to the conventions directory.

        Returns:
            The full path to the conventions directory or subdirectory.
        """
        base = self.config_path("conventions")
        return self.join_paths(base, path)

    def is_development(self) -> bool:
        """
        Determine if the application is in the local environment.

        Returns:
            True if in local environment, False otherwise.
        """
        return self["env"] == "development" or self["env"] == "dev"

    def is_production(self) -> bool:
        """
        Determine if the application is in the production environment.

        Returns:
            True if in production environment, False otherwise.
        """
        return self["env"] == "production"

    def running_unit_tests(self) -> bool:
        """
        Determine if the application is running unit tests.

        Returns:
            True if running unit tests, False otherwise.
        """
        return self["env"] == "testing"

    def detect_environment(self, callback: Callable) -> str:
        """
        Detect the application's current environment.

        Args:
            callback: Closure that returns the environment name.

        Returns:
            Environment name.
        """
        from byte.foundation.environment_detector import EnvironmentDetector

        env = EnvironmentDetector().detect(callback, self)
        self.instance("env", env)
        return env

    def environment_path(self) -> Path:
        """
        Get the path to the environment file directory.

        Returns:
            The full path to the environment file directory.
        """
        environment_path = getattr(self, "_environment_path", None)
        return Path(environment_path) if environment_path else self.root_path()

    def environment_file_path(self) -> Path:
        """
        Get the fully qualified path to the environment file.

        Returns:
            The full path to the environment file.
        """
        return self.join_paths(self.environment_path(), ".env")

    def session_context_path(self, path: str = "") -> Path:
        """
        Get the path to the session context directory.

        Args:
            path: Optional path to append to the session context directory.

        Returns:
            The full path to the session context directory or subdirectory.
        """
        base = self.config_path("session_context")
        return self.join_paths(base, path)

    def join_paths(self, base_path: str | Path, path: str = "") -> Path:
        """
        Join the given paths together.

        Args:
            base_path: The base path.
            path: The path to join (optional).

        Returns:
            The joined path as a Path object.
        """

        base = Path(base_path)
        if path:
            return base / path
        return base

    def has_been_bootstrapped(self) -> bool:
        """
        Determine if the application has been bootstrapped before.

        Returns:
            True if bootstrapped, False otherwise.
        """
        return self._has_been_bootstrapped

    async def handle_command(self, input: list[str]) -> int:
        # dispatcher = self.make(Dispatcher)
        kernel = self.make(Kernel, app=self)
        status = await kernel.handle(input)
        kernel.terminate()

        return status

    async def run(self) -> int:
        """Run the interactive prompt-based application loop.

        Usage: `await app.run()` -> starts interactive session until KeyboardInterrupt
        """
        from byte.cli import PromptToolkitService

        input_service = self.make(PromptToolkitService)
        while True:
            try:
                await input_service.execute()
            except KeyboardInterrupt:
                break
            # except Exception as e:
            # TODO: I think this can be moved to the general Exception handler.
            # log.exception(e)
            # console = self.app["console"]
            # console.print_error_panel(
            #     str(e),
            #     title="Exception",
            # )
            # return 2
        return 1

    def terminate(self) -> None:
        """Terminate the application."""
        pass

    def register(self, provider) -> ServiceProvider:
        """
        Register a service provider with the application.

        """

        # Check that provider extends ServiceProvider
        if not (inspect.isclass(provider) and issubclass(provider, ServiceProvider)):
            raise TypeError(
                f"Provider {provider.__name__ if inspect.isclass(provider) else provider} must extend ServiceProvider"
            )

        self.singleton(provider)

        # Instantiate the provider
        provider = self.make(provider, app=self)

        # Call the register method if it exists
        if hasattr(provider, "register") and callable(provider.register):
            provider.register()

        # # Call the register services method if it exists
        if hasattr(provider, "register_services") and callable(provider.register_services):
            provider.register_services()

        # Call the register services method if it exists
        if hasattr(provider, "register_commands") and callable(provider.register_commands):
            provider.register_commands()

        return provider

    def dispatch_task(self, coro):
        """Dispatch a fire-and-forget background task with auto-generated name.

        Usage: `app.dispatch_task(some_async_function())` -> starts task in background
        """
        task_manager = self.make(TaskManager)
        return task_manager.dispatch_task(coro)
