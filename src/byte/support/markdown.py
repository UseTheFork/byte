class MD:
    """Markdown helper utilities."""

    @staticmethod
    def bullet(text: str, level: int = 1) -> str:
        indent = "  " * level
        stripped = text.strip()
        # Remove existing bullet prefixes if present
        for prefix in ("- ", "* ", "+ "):
            if stripped.startswith(prefix):
                stripped = stripped[len(prefix) :].strip()
                break
        return f"{indent}- {stripped.strip()}"

    @staticmethod
    def bullet_list(lines: list[str], level: int = 1) -> str:
        """Create a bullet for the first line and indent remaining lines."""
        if not lines:
            return ""
        indent = "  " * level
        result = []
        for i, line in enumerate(lines):
            if i == 0:
                # First line gets the bullet
                stripped = line.strip()
                for prefix in ("- ", "* ", "+ "):
                    if stripped.startswith(prefix):
                        stripped = stripped[len(prefix) :].strip()
                        break
                result.append(f"{indent}- {stripped.strip()}")
            else:
                # Remaining lines get indented
                result.append(f"{indent}  {line.strip()}")
        return "\n".join(result)

    @staticmethod
    def list_to_text(lines: list[str], seperator: str = "\n") -> str:
        """
        Convert a list of strings into a single multi-line string.

        Example:
            ["foo", "bar", "baz"] -> "foo\nbar\nbaz"
        """
        if not lines:
            return ""

        return seperator.join(lines)

    @staticmethod
    def clean_comment_lines(lines: list[str] | str) -> str:
        """Clean comment lines by removing leading comment markers.

        Accepts either a list of strings or a single string (which gets split into lines).
        Removes leading comment markers (/, #, -, ;) from each line using lstrip.
        Returns cleaned lines joined by newlines.

        Example:
            ["# foo", "// bar"] -> "foo\nbar"
            "# foo\n// bar" -> "foo\nbar"
        """
        if isinstance(lines, str):
            lines = lines.split("\n")

        result = [line.lstrip("/#-;").strip() for line in lines]
        return "\n".join(result)
