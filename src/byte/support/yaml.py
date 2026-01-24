from pathlib import Path
from typing import Any, Dict

import yaml


class Yaml:
    """YAML helper utilities."""

    @staticmethod
    def load(path: str | Path) -> Any:
        """Load a YAML file and return its contents.

        Args:
            path: Path to the YAML file.

        Returns:
            The parsed YAML content.

        Usage: `data = Yaml.load("config.yaml")`
        """
        path = Path(path)
        if not path.exists():
            return None

        with open(path) as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_as_dict(path: str | Path) -> Dict[str, Any]:
        """Load a YAML file and return it as a dictionary.

        Args:
            path: Path to the YAML file.

        Returns:
            The parsed YAML content as a dictionary, or empty dict if None.

        Usage: `config = Yaml.load_as_dict("config.yaml")`
        """
        data = Yaml.load(path)
        return data if isinstance(data, dict) else {}

    @staticmethod
    def save(path: str | Path, data: Dict[str, Any]) -> None:
        """Save data to a YAML file.

        Args:
            path: Path to the YAML file.
            data: The data to save.

        Usage: `Yaml.save("config.yaml", config_dict)`
        """
        path = Path(path)
        with open(path, "w") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
