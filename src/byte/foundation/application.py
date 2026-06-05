import inspect
from pathlib import Path
from typing import Callable, Optional, TypeVar

from git import InvalidGitRepositoryError, Repo
from textual.message import Message

from byte import ServiceProvider, TaskManager
from byte.foundation import Container, FoundationServiceProvider, Kernel
from byte.foundation.bootstrap import RegisterProviders
from byte.logging import LogService, LogServiceProvider
from byte.tui import ByteTUI, Console

T = TypeVar("T")


class Application(Container):
    """Manage service providers and the application lifecycle."""

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
        """Register base service provider instances in the container."""
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
        """Set the Git repository root path by traversing up from the start path."""
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
        """Register a new boot listener."""
        self._booting_callbacks.append(callback)

    def booted(self, callback: Callable):
        """Register a new "booted" listener."""
        self._booted_callbacks.append(callback)

        # TODO: need to figure out how to make this async friendly
        if self.is_booted():
            callback(self)

    def is_booted(self) -> bool:
        """Determine if the application has been booted."""
        return self._booted

    async def boot(self) -> None:
        """Boot the application's service providers."""
        if self.is_booted():
            return

        # Fire booting callbacks
        for callback in self._booting_callbacks:
            callback(self)

        providers = RegisterProviders._merge

        # TODO: Use gather here?
        for provider in providers:
            provider_instance = self.make(provider)
            await self.boot_provider(provider_instance)  # ty:ignore[invalid-argument-type]

        # Fire booted callbacks
        for callback in self._booted_callbacks:
            if inspect.iscoroutinefunction(callback):
                await callback(self)
            else:
                callback(self)

        self._booted = True

    async def boot_provider(self, provider: ServiceProvider) -> None:
        """Boot a service provider."""
        if hasattr(provider, "boot") and callable(getattr(provider, "boot")):
            await provider.boot()

    def bind_paths_in_container(self):
        """Bind path instances to the container."""
        self.instance("path", self.root_path())
        self.instance("path.app", self.app_path())
        self.instance("path.root", self.root_path())
        self.instance("path.config", self.config_path())
        self.instance("path.cache", self.cache_path())
        self.instance("path.conventions", self.conventions_path())
        self.instance("path.session_context", self.session_context_path())
        self.instance("path.specs", self.specs_path())

        return self

    def log(self) -> LogService:
        """Get the Log service instance from the container."""
        return self.make(LogService)

    def tui(self) -> ByteTUI:
        """Get the ByteTUI instance from the container."""
        return self.make(ByteTUI)

    def console(self) -> Console:
        """Get the Console instance from the container."""
        return self.make(Console)

    def path(self, path: str = "") -> Path:
        """Get the path to the "root" directory."""
        return self.join_paths(self.root_path(), path)

    def app_path(self, path: str = "") -> Path:
        """Get the path to the Byte application installation."""
        byte_package_path = Path(__file__).parent.parent
        return self.join_paths(byte_package_path, path)

    def base_path(self, path: str = "") -> Path:
        """Get the base path of the application installation."""
        return self.join_paths(self._base_path, path)

    def root_path(self, path: str = "") -> Path:
        """Get the root path of the Git repository."""
        return self.join_paths(self._git_root_path, path)

    def config_path(self, path: str = "") -> Path:
        """Get the path to the application configuration directory."""
        base = self.root_path(".byte")
        return self.join_paths(base, path)

    def cache_path(self, path: str = "") -> Path:
        """Get the path to the application cache directory."""
        base = self.config_path("cache")
        return self.join_paths(base, path)

    def conventions_path(self, path: str = "") -> Path:
        """Get the path to the conventions directory."""
        base = self.config_path("conventions")
        return self.join_paths(base, path)

    def skills_path(self, path: str = "") -> Path:
        """Get the path to the skills directory."""
        base = self.config_path("skills")
        return self.join_paths(base, path)

    def specs_path(self, path: str = "") -> Path:
        """Get the path to the specs directory."""
        base = self.config_path("specs")
        return self.join_paths(base, path)

    def is_development(self) -> bool:
        """Determine if the application is in the local environment."""
        return self["env"] == "development" or self["env"] == "dev"

    def is_production(self) -> bool:
        """Determine if the application is in the production environment."""
        return self["env"] == "production"

    def running_unit_tests(self) -> bool:
        """Determine if the application is running unit tests."""
        return self["env"] == "testing"

    def detect_environment(self, callback: Callable) -> str:
        """Detect the application's current environment."""
        from byte.foundation.environment_detector import EnvironmentDetector

        env = EnvironmentDetector().detect(callback, self)
        self.instance("env", env)
        return env

    def environment_path(self) -> Path:
        """Get the path to the environment file directory."""
        environment_path = getattr(self, "_environment_path", None)
        return Path(environment_path) if environment_path else self.root_path()

    def environment_file_path(self) -> Path:
        """Get the fully qualified path to the environment file."""
        return self.join_paths(self.environment_path(), ".env")

    def session_context_path(self, path: str = "") -> Path:
        """Get the path to the session context directory."""
        base = self.config_path("session_context")
        return self.join_paths(base, path)

    def join_paths(self, base_path: str | Path, path: str = "") -> Path:
        """Join the given paths together."""
        base = Path(base_path)
        if path:
            return base / path
        return base

    def has_been_bootstrapped(self) -> bool:
        """Determine if the application has been bootstrapped before."""
        return self._has_been_bootstrapped

    async def handle_command(self, input: list[str]) -> int:
        """Handle a command input and return the status code."""
        # dispatcher = self.make(Dispatcher)
        try:
            kernel = self.make(Kernel, app=self)
            status = await kernel.handle(input)
            kernel.terminate()
        except KeyboardInterrupt:
            pass

        return status

    async def run(self) -> int:
        """Run the interactive prompt-based application loop."""
        from byte.tui import TUIManagerService

        # TODO: This needs to be fixed / updates
        try:
            tui = self.make(TUIManagerService)

            await tui.run_async()
        except Exception:
            return 2

        return 1

        # from byte.cli import PromptToolkitService

        # input_service = self.make(PromptToolkitService)
        # while True:
        #     try:
        #         await input_service.execute()
        #     except KeyboardInterrupt:
        #         break
        #     # except Exception as e:
        #     # TODO: I think this can be moved to the general Exception handler.
        #     # log.exception(e)
        #     # console = self.app["console"]
        #     # console.print_error_panel(
        #     #     str(e),
        #     #     title="Exception",
        #     # )
        #     # return 2
        # return 1

    def terminate(self) -> None:
        """Terminate the application."""
        pass

    def register(self, provider) -> ServiceProvider:
        """Register a service provider with the application."""
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

        if hasattr(provider, "register_tools") and callable(provider.register_tools):
            provider.register_tools()

        if hasattr(provider, "register_nodes") and callable(provider.register_nodes):
            provider.register_nodes()

        if hasattr(provider, "register_agents") and callable(provider.register_agents):
            provider.register_agents()

        if hasattr(provider, "register_workflows") and callable(provider.register_workflows):
            provider.register_workflows()

        return provider

    def dispatch_task(self, coro):
        """Dispatch a fire-and-forget background task with auto-generated name."""
        task_manager = self.make(TaskManager)
        return task_manager.dispatch_task(coro)

    def emit_tui(self, payload: Message) -> str | None:
        """Emit a TUI message and return its panel ID."""
        if hasattr(payload, "panel_id"):
            from byte.tui import TUIManagerService

            tui_manager_service = self.make(TUIManagerService)
            payload.panel_id = tui_manager_service.get_panel_id()  # ty:ignore[invalid-assignment]

        byte_tui = self.tui()
        byte_tui.conversation.post_message(payload)

        return getattr(payload, "panel_id", None)
