import re
from pathlib import Path
from typing import Any, Dict

import yaml

_FRONTMATTER_RE = re.compile(r"^---[\r\n]+(.*?)[\r\n]+---", re.DOTALL | re.MULTILINE)


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

    @staticmethod
    def parse_frontmatter(text: str) -> tuple[dict, str]:
        """Parse a Markdown file into (frontmatter dict, body string).

        Extracts YAML frontmatter between opening and closing ``---`` fences
        at the start of the file. Returns an empty dict when no YAML block
        is found.

        Args:
            text: Raw file content.

        Returns:
            ``(frontmatter, body)`` where *frontmatter* is an empty dict when
            no YAML block is found and *body* is the remaining content after
            the closing ``---``.

        Usage: `fm, body = Yaml.parse_frontmatter(content)`
        """
        match = _FRONTMATTER_RE.match(text)
        if not match:
            return {}, text.strip()
        fm = yaml.safe_load(match.group(1)) or {}
        body = text[match.end() :].strip()
        return fm, body

    @staticmethod
    def render_frontmatter(frontmatter: dict, body: str = "") -> str:
        """Render a Markdown file with YAML frontmatter.

        Serializes a dictionary as YAML between ``---`` fences, optionally
        followed by a Markdown body.

        Args:
            frontmatter: Mapping to serialise as YAML between ``---`` fences.
            body:        Optional Markdown body appended after the closing fence.

        Returns:
            Complete file content string.

        Usage: `content = Yaml.render_frontmatter({"key": "value"}, "body text")`
        """
        fm = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True).rstrip()
        parts = [f"---\n{fm}\n---"]
        if body:
            parts.append(body.strip())
        return "\n".join(parts) + "\n"

    @staticmethod
    def parse_frontmatter_file(path: str | Path) -> tuple[dict, str]:
        """Parse a Markdown file with frontmatter from disk.

        Convenience method combining file read and frontmatter parsing.

        Args:
            path: Path to the file.

        Returns:
            ``(frontmatter, body)`` tuple from parsing the file content.

        Usage: `fm, body = Yaml.parse_frontmatter_file("path/to/file.md")`
        """
        path = Path(path)
        content = path.read_text(encoding="utf-8")
        return Yaml.parse_frontmatter(content)
