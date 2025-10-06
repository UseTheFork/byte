import yaml

from byte.core.config.config import BYTE_CONFIG_FILE


class FirstBootInitializer:
    """Handle first-time setup and configuration for Byte.

    Detects if this is the first run and guides users through initial
    configuration, creating necessary files and directories.
    Usage: `initializer = FirstBootInitializer()`
           `await initializer.run_if_needed()`
    """

    # Default configuration template for first boot
    # This will be written to .byte/config.yaml
    CONFIG_TEMPLATE = {
        "model": "sonnet",
        "lint": {
            "enabled": True,
        },
    }

    def __init__(self):
        pass

    def is_first_boot(self) -> bool:
        """Check if this is the first time Byte is being run.

        Usage: `if await initializer.is_first_boot(): ...`
        """
        return not BYTE_CONFIG_FILE.exists()

    def run_if_needed(self) -> bool:
        """Run initialization flow if this is the first boot.

        Returns True if initialization was performed, False if skipped.
        Usage: `initialized = await initializer.run_if_needed()`
        """
        if not self.is_first_boot():
            return False

        self._run_initialization()
        return True

    def _run_initialization(self) -> None:
        """Perform first-boot initialization steps.

        Creates the default configuration file from the template.
        """
        # Ensure the .byte directory exists
        BYTE_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Write the configuration template to the YAML file
        with open(BYTE_CONFIG_FILE, "w") as f:
            yaml.dump(
                self.CONFIG_TEMPLATE,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )

        print(f"✓ Created configuration file at {BYTE_CONFIG_FILE}")
        print("  You can customize your settings by editing this file.")
