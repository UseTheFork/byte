import shutil
from typing import TYPE_CHECKING

from byte.config import ByteConfig, ByteUserConfig
from byte.foundation.bootstrap.bootstrapper import Bootstrapper
from byte.llm.config import LLMModelConfig
from byte.support import Json, Yaml
from byte.tui.rich.menu import Menu

if TYPE_CHECKING:
    from byte import Application


class PrepareEnvironment(Bootstrapper):
    """Prepare the environment for Byte on first run and subsequent boots."""

    def _migrate_yaml_to_jsonc(self, app: Application) -> None:
        """Migrate config.yaml to config.jsonc if it exists."""
        yaml_path = app.config_path("config.yaml")
        jsonc_path = app.config_path("config.jsonc")

        if yaml_path.exists():
            data = {
                "$schema": "https://raw.githubusercontent.com/UseTheFork/byte/refs/heads/main/schema.json",
                **Yaml.load_as_dict(yaml_path),
            }
            Json.save(jsonc_path, data)
            yaml_path.unlink()
            app["console"].print_boot_status("ok", "Migrated config.yaml to config.jsonc")

    def _prepare_directories(self, app: Application):
        """Prepare session context and cache directories for the current boot."""

        session_context_path = app.session_context_path()

        # Delete and recreate session_context to ensure it's empty on each boot
        if session_context_path.exists():
            shutil.rmtree(session_context_path)
        session_context_path.mkdir(exist_ok=True)

        app.cache_path().mkdir(exist_ok=True)

    def _init_files(self, app: Application, config: ByteConfig) -> ByteConfig:
        """Initialize files configuration by prompting the user to enable file watching."""

        menu = Menu(
            title="Enable file watching for AI comment markers (AI:, AI@, AI?, AI!)?", console=app["console"].console
        )
        enable_watch = menu.confirm(default=False)

        if enable_watch:
            config.files.watch.enable = True
            app["console"].print_success("File watching enabled\n")
        else:
            config.files.watch.enable = False
            app["console"].print_info("File watching disabled\n")

        return config

    def _init_llm(self, app: Application, config: ByteConfig) -> ByteConfig:
        """Initialize LLM configuration by prompting the user to select a provider."""

        # Build list of enabled providers
        providers = [
            "anthropic",
            "gemini",
            "openai",
        ]

        # Multiple providers available - ask user to choose
        app["console"].print_info("Please choose a default provider:\n")
        menu = Menu(*providers, title="Select LLM Provider", console=app["console"].console)
        selected = menu.select()

        if selected is None:
            # User cancelled - default to first available
            selected = providers[0]
            app["console"].print_warning(f"No selection made, defaulting to {selected}\n")
        else:
            app["console"].print_success(f"Selected {selected} as LLM provider\n")

        if selected == "anthropic":
            config.llm.reasoning = LLMModelConfig(model="claude-opus-4-6", provider="anthropic")
            config.llm.standard = LLMModelConfig(model="claude-sonnet-4-6", provider="anthropic")
            config.llm.coding = LLMModelConfig(model="claude-haiku-4-5", provider="anthropic")
            config.llm.fast = LLMModelConfig(model="claude-haiku-4-5", provider="anthropic")
        elif selected == "gemini":
            config.llm.reasoning = LLMModelConfig(model="gemini-3.1-pro-preview", provider="gemini")
            config.llm.standard = LLMModelConfig(model="gemini-3.5-flash", provider="gemini")
            config.llm.coding = LLMModelConfig(model="gemini-3.5-flash", provider="gemini")
            config.llm.fast = LLMModelConfig(model="gemini-3.5-flash", provider="gemini")
        else:
            config.llm.reasoning = LLMModelConfig(model="gpt-5.5", provider="openai")
            config.llm.standard = LLMModelConfig(model="gpt-5.4", provider="openai")
            config.llm.coding = LLMModelConfig(model="gpt-5.4-mini", provider="openai")
            config.llm.fast = LLMModelConfig(model="gpt-5.4-mini", provider="openai")
        return config

    def _setup_config(self, app: Application) -> None:
        """Set up the initial Byte configuration file with LLM and file watching preferences."""

        # TODO: need to make choosing a LLM smarter. Should load and let user select a provider if they want to.

        # Build config with selected LLM model
        config = ByteConfig()

        # Initialize files configuration
        config = self._init_files(app, config)

        # Initialize LLM configuration
        config = self._init_llm(app, config)

        # Write the configuration template to the JSONC file
        config_path = app.config_path("config.jsonc")

        user_fields = set(ByteUserConfig.model_fields.keys())
        data = {
            "$schema": "https://raw.githubusercontent.com/UseTheFork/byte/refs/heads/main/schema.json",
            **config.model_dump(mode="json", include=user_fields),
        }
        Json.save(config_path, data)

        app["console"].print_success(f"Created configuration file at {config_path}\n")

    def _setup_byte_directories(self, app: Application) -> None:
        """Set up all necessary Byte directories."""

        # Ensure the main .byte directory exists
        app.config_path().parent.mkdir(parents=True, exist_ok=True)

        # Create conventions directory for style guides and project conventions
        app.conventions_path().parent.mkdir(parents=True, exist_ok=True)

        # Create context directory for style guides and project context
        app.session_context_path().parent.mkdir(parents=True, exist_ok=True)

        # Create cache directory for temporary files
        app.cache_path().parent.mkdir(parents=True, exist_ok=True)

        app["console"].print_boot_status("ok", "Created Byte directories")

    def _setup_gitignore(self, app: Application) -> None:
        """Set up .gitignore in the .byte config directory with cache and session patterns."""

        gitignore_path = app.config_path(".gitignore")
        byte_patterns = ["cache/*", "session_context/*"]
        gitignore_content = "\n".join(byte_patterns) + "\n"

        gitignore_path.write_text(gitignore_content)

    def _run_first_boot_setup(self, app: Application) -> None:
        """Run first-boot setup tasks including directory and configuration initialization."""
        self._setup_byte_directories(app)
        self._setup_config(app)

    def bootstrap(self, app: Application) -> None:
        """Prepare the environment on boot, including first-boot setup if needed."""

        # Temporary here to convert old yaml config to jsonc config
        self._migrate_yaml_to_jsonc(app)

        self._prepare_directories(app)
        self._setup_gitignore(app)

        if self.is_first_boot(app):
            self._run_first_boot_setup(app)

    def is_first_boot(self, app: Application) -> bool:
        """Check if this is the first time Byte is being run."""

        return not app.config_path("config.jsonc").exists()
