def merge_classes(*class_strings: str | None) -> str:
    """Merge multiple class strings into a single space-separated string.

    Filters out None values and empty strings, then combines all classes.
    Usage: `merge_classes("foo bar", None, "baz")` -> "foo bar baz"
    """
    return " ".join(cls for cls in class_strings if cls)
