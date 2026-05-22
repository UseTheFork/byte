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
