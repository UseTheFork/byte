class EditFormatError(Exception):
    """Base exception for edit format operations."""

    pass


class PreFlightCheckError(EditFormatError):
    """Exception raised when pre-flight validation of edit blocks fails.

    This indicates malformed or invalid edit block structure that would
    prevent successful parsing and application of edits.
    """

    pass


class PreFlightUnparsableError(EditFormatError):
    """Exception raised when edit blocks cannot be parsed from the content.

    This indicates the content contains malformed edit block syntax that
    prevents the parser from extracting valid edit operations.
    """

    pass


class NoBlocksFoundError(EditFormatError):
    """Exception raised when no SEARCH/REPLACE blocks are found in content.

    This indicates the AI response did not contain any edit blocks,
    which may be intentional (e.g., conversational response only).
    """

    pass


class ReadOnlyFileError(EditFormatError):
    """Exception raised when attempting to edit a read-only file.

    This indicates an attempt to modify a file that is in read-only context,
    which is not permitted by the system.
    """

    pass


class SearchContentNotFoundError(EditFormatError):
    """Exception raised when search content cannot be found in the target file.

    This indicates the search block content does not match any content
    in the specified file, preventing the edit operation.
    """

    pass


class FileOutsideProjectError(EditFormatError):
    """Exception raised when attempting to create a file outside the git root.

    This indicates an attempt to create a new file in a location that is
    outside the project's git repository root directory.
    """

    pass
