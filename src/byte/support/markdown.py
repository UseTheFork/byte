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
