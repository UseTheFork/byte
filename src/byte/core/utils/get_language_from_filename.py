from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound


def get_language_from_filename(filename: str) -> str | None:
    """Get the language name for a file using Pygments lexer detection.

    Args:
            filename: Filename or path to analyze

    Returns:
            Language name (e.g., 'Python', 'JavaScript') or None if not detected

    Usage: `lang = get_language_from_filename('script.py')` -> 'Python'
    """

    try:
        lexer = get_lexer_for_filename(filename)
        return lexer.name.lower()
    except ClassNotFound:
        return None
