def list_to_multiline_text(lines: list[str], seperator: str = "\n") -> str:
    """
    Convert a list of strings into a single multi-line string.

    Example:
        ["foo", "bar", "baz"] -> "foo\nbar\nbaz"
    """
    if not lines:
        return ""

    return seperator.join(lines)
