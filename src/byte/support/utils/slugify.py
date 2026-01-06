def slugify(text: str, separator: str = "-") -> str:
    """Convert a string to a URL-safe slug format.

    Converts text to lowercase, replaces non-alphanumeric characters with
    the specified separator, and removes leading/trailing separators. Useful for creating
    keys from URLs or arbitrary text.
    Usage: `key = slugify("https://example.com/page")` -> "https-example-com-page"
    Usage: `key = slugify("Hello World", "_")` -> "hello_world"
    """
    import re

    # Convert to lowercase
    text = text.lower()
    # Replace non-alphanumeric characters with separator
    text = re.sub(r"[^a-z0-9]+", separator, text)
    # Remove leading/trailing separators
    text = text.strip(separator)
    return text
