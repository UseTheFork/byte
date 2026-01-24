from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional

from byte.cli import Menu
from byte.config import ByteConfig
from byte.foundation.bootstrap.bootstrapper import Bootstrapper
from byte.support import Yaml

if TYPE_CHECKING:
    from byte.foundation import Application


class PrepareEnvironment(Bootstrapper):
    """"""

    def _prepare_directories(self, app: Application):
        """Check if this is the first time Byte is being run.

        Usage: `if await initializer.is_first_boot(): ...`
        """

        session_context_path = app.session_context_path()

        # Delete and recreate session_context to ensure it's empty on each boot
        if session_context_path.exists():
            shutil.rmtree(session_context_path)
        session_context_path.mkdir(exist_ok=True)

        app.cache_path().mkdir(exist_ok=True)
        app.conventions_path().mkdir(exist_ok=True)

    def _find_binary(self, binary_name: str) -> Optional[Path]:
        """Find the full path to a binary using which.

        Returns the absolute path to the binary if found, None otherwise.
        Usage: `chrome_path = initializer.find_binary("google-chrome")`
        Usage: `python_path = initializer.find_binary("python3")` -> Path("/usr/bin/python3")
        """
        result = shutil.which(binary_name)
        return Path(result) if result else None

    def _init_web(self, app: Application, config: ByteConfig) -> ByteConfig:
        """Initialize web configuration by detecting Chrome or Chromium binary.

        Attempts to locate google-chrome-stable first, then falls back to chromium.
        Updates the chrome_binary_location in the web config section.
        Usage: `config = initializer._init_web(config)`
        """
        chrome_path = self._find_binary("google-chrome-stable")
        if chrome_path is None:
            chrome_path = self._find_binary("chromium")

        if chrome_path is not None:
            config.web.chrome_binary_location = chrome_path
            config.web.enable = True
            browser_name = "Chrome" if "chrome" in str(chrome_path) else "Chromium"
            app["console"].print_success(f"Found {browser_name} at {chrome_path}")
            app["console"].print_success("Web commands enabled\n")
        else:
            app["console"].print_warning("Chromium binary not found")
            app["console"].print_warning("Web commands are disabled\n")

        return config

    def _init_files(self, app: Application, config: ByteConfig) -> ByteConfig:
        """Initialize files configuration by asking if user wants to enable file watching.

        Prompts user with a confirmation dialog. If confirmed, sets watch.enable to true.
        Usage: `config = initializer._init_files(config)`
        """

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

    def _init_llm(self, app: Application) -> Literal["anthropic", "gemini", "openai"]:
        """Initialize LLM configuration by asking user to choose a provider.

        Only shows providers that are enabled (have API keys set).
        Returns the selected provider name.
        Usage: `model = initializer._init_llm()` -> "anthropic"
        """

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

        return selected  # ty:ignore[invalid-return-type]

    def _setup_config(self, app: Application) -> None:
        # Initialize LLM configuration
        # llm_model = self._init_llm(app)

        # TODO: need to make choosing a LLM smarter. Should load and let user select a provider if they want to.

        # Build config with selected LLM model
        config = ByteConfig()

        # Initialize files configuration
        config = self._init_files(app, config)

        # Initialize web configuration
        config = self._init_web(app, config)

        # Write the configuration template to the YAML file

        config_path = app.config_path("config.yaml")
        Yaml.save(config_path, config.model_dump(mode="json"))

        app["console"].print_success(f"Created configuration file at {config_path}\n")

    def _setup_byte_directories(self, app: Application) -> None:
        """Set up all necessary Byte directories.

        Creates .byte, .byte/conventions, and .byte/cache directories.
        Usage: `initializer._setup_byte_directories()`
        """

        # Ensure the main .byte directory exists
        app.config_path().parent.mkdir(parents=True, exist_ok=True)

        # Create conventions directory for style guides and project conventions
        app.conventions_path().parent.mkdir(parents=True, exist_ok=True)

        # Create context directory for style guides and project context
        app.session_context_path().parent.mkdir(parents=True, exist_ok=True)

        # Create cache directory for temporary files
        app.cache_path().parent.mkdir(parents=True, exist_ok=True)

        app["console"].print_success("Created Byte directories")

    def _setup_gitignore(self, app: Application):
        """Ensure .gitignore exists and contains byte cache and session patterns.

        Usage: `config = self._apply_gitignore_config(config)`
        """
        gitignore_path = app.path(".gitignore")

        byte_patterns = [".byte/cache/*", ".byte/session_context/*"]

        # Check if .gitignore exists
        if gitignore_path.exists():
            # Read existing content
            content = gitignore_path.read_text()

            # Check which patterns are missing
            missing_patterns = [pattern for pattern in byte_patterns if pattern not in content]

            if missing_patterns:
                # Ask user if they want to add missing patterns to gitignore
                patterns_str = ", ".join(missing_patterns)
                menu = Menu(title=f"Add {patterns_str} to .gitignore?", console=app["console"].console)
                add_to_gitignore = menu.confirm(default=True)

                if add_to_gitignore:
                    # Add missing patterns
                    with open(gitignore_path, "a") as f:
                        # Add newline if file doesn't end with one
                        if content and not content.endswith("\n"):
                            f.write("\n")
                        f.writelines(f"{pattern}\n" for pattern in missing_patterns)
                    app["console"].print_success(f"Added {patterns_str} to .gitignore\n")
                else:
                    app["console"].print_info("Skipped adding patterns to .gitignore\n")
        else:
            # Ask user if they want to create .gitignore with byte patterns
            menu = Menu(title="Create .gitignore with .byte patterns?", console=app["console"].console)
            create_gitignore = menu.confirm(default=True)

            if create_gitignore:
                # Create .gitignore with byte patterns
                gitignore_content = "\n".join(byte_patterns) + "\n"
                gitignore_path.write_text(gitignore_content)
                app["console"].print_success("Created .gitignore with .byte patterns\n")
            else:
                app["console"].print_info("Skipped creating .gitignore\n")

    def _run_first_boot_setup(self, app: Application):
        app["console"].print_info("\n[bold cyan]Welcome to Byte![/bold cyan]")
        app["console"].print_info("Setting up your development environment...\n")

        self._setup_byte_directories(app)
        self._setup_gitignore(app)
        self._setup_config(app)

    def bootstrap(self, app: Application) -> None:
        """ """

        self._prepare_directories(app)

        if self.is_first_boot(app):
            self._run_first_boot_setup(app)

    def is_first_boot(self, app: Application) -> bool:
        """Check if this is the first time Byte is being run.

        Usage: `if await initializer.is_first_boot(): ...`
        """

        return not app.config_path("config.yaml").exists()
