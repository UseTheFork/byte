import json
from pathlib import Path
from typing import Any, Dict

import jsonc


class Json:
    """JSONC helper utilities."""

    @staticmethod
    def load(path: str | Path) -> Any:
        """Load a JSONC file and return its contents.

        Args:
            path: Path to the JSONC file.

        Returns:
            The parsed JSONC content.

        Usage: `data = Json.load("config.jsonc")`
        """
        path = Path(path)
        if not path.exists():
            return None

        with open(path) as f:
            return jsonc.loads(f.read())

    @staticmethod
    def load_as_dict(path: str | Path) -> Dict[str, Any]:
        """Load a JSONC file and return it as a dictionary.

        Args:
            path: Path to the JSONC file.

        Returns:
            The parsed JSONC content as a dictionary, or empty dict if None.

        Usage: `config = Json.load_as_dict("config.jsonc")`
        """
        data = Json.load(path)
        return data if isinstance(data, dict) else {}

    @staticmethod
    def save(path: str | Path, data: Dict[str, Any]) -> None:
        """Save data to a JSON file.

        Args:
            path: Path to the JSON file.
            data: The data to save.

        Usage: `Json.save("config.jsonc", config_dict)`
        """
        path = Path(path)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
