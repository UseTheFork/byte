from byte.config.migrator import BaseMigration


class Migration(BaseMigration):
    """Migrate config to version 1.0.0."""

    @property
    def target_version(self) -> str:
        return "1.0.0"

    def migrate(self, config: dict) -> dict:
        """Apply changes for 1.0.0."""

        if "llm" not in config:
            config["llm"] = {}

        if "model" in config["llm"]:
            old_model = config["llm"]["model"]

            if "main_model" not in config["llm"]:
                config["llm"]["main_model"] = {}

            if "weak_model" not in config["llm"]:
                config["llm"]["weak_model"] = {}

            config["llm"]["main_model"]["model"] = old_model
            config["llm"]["weak_model"]["model"] = old_model

            del config["llm"]["model"]

        # Update version
        config["version"] = self.target_version
        return config
