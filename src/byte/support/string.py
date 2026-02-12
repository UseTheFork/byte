import re


class Str:
    """String helper utilities."""

    @staticmethod
    def parse_callback(callback: str, default: str | None = None) -> tuple[str, str | None]:
        """
        Parse a Class:method style callback into class and method.

        Args:
            callback: Callback string in format 'Class:method'.
            default: Default method name if not specified.

        Returns:
            Tuple of (class_name, method_name).
        """
        if Str.contains(callback, ":anonymous\0"):
            if Str.substr_count(callback, ":") > 1:
                return (
                    Str.before_last(callback, ":"),
                    Str.after_last(callback, ":"),
                )

            return (callback, default)

        if Str.contains(callback, ":"):
            parts = callback.split(":", 1)
            return (parts[0], parts[1])
        return (callback, default)

    @staticmethod
    def contains(haystack: str | None, needles: str | list[str], ignore_case: bool = False) -> bool:
        """
        Determine if a given string contains a given substring.

        Args:
            haystack: The string to search in.
            needles: The substring(s) to search for.
            ignore_case: Whether to ignore case.

        Returns:
            True if any needle is found, False otherwise.
        """
        if haystack is None:
            return False

        if ignore_case:
            haystack = haystack.lower()

        if not isinstance(needles, list):
            needles = [needles]

        for needle in needles:
            if ignore_case:
                needle = needle.lower()

            if needle != "" and needle in haystack:
                return True

        return False

    @staticmethod
    def substr_count(haystack: str, needle: str, offset: int = 0, length: int | None = None) -> int:
        """
        Returns the number of substring occurrences.

        Args:
            haystack: The string to search in.
            needle: The substring to search for.
            offset: The offset where to start counting.
            length: The maximum length after the offset to search for.

        Returns:
            Number of occurrences.
        """
        if length is not None:
            return haystack[offset : offset + length].count(needle)

        return haystack[offset:].count(needle)

    @staticmethod
    def before_last(subject: str, search: str) -> str:
        """
        Get the portion of a string before the last occurrence of a given value.

        Args:
            subject: The string to search in.
            search: The value to search for.

        Returns:
            The portion before the last occurrence, or the original string if not found.
        """
        if search == "":
            return subject

        pos = subject.rfind(search)

        if pos == -1:
            return subject

        return subject[:pos]

    @staticmethod
    def after_last(subject: str, search: str) -> str:
        """
        Return the remainder of a string after the last occurrence of a given value.

        Args:
            subject: The string to search in.
            search: The value to search for.

        Returns:
            The portion after the last occurrence, or the original string if not found.
        """
        if search == "":
            return subject

        position = subject.rfind(search)

        if position == -1:
            return subject

        return subject[position + len(search) :]

    @staticmethod
    def substr(string: str, start: int, length: int | None = None) -> str:
        """
        Returns the portion of the string specified by the start and length parameters.

        Args:
            string: The input string.
            start: The start position.
            length: The length of the substring.

        Returns:
            The extracted substring.
        """
        if length is None:
            return string[start:]
        elif length >= 0:
            return string[start : start + length]
        else:
            return string[start:length]

    @staticmethod
    def class_to_string(abstract: str | type) -> str:
        """
        Normalize abstract type to string representation.

        Args:
            abstract: Abstract type identifier or class.

        Returns:
            String representation of the abstract type.
        """
        if isinstance(abstract, type):
            return f"{abstract.__module__}.{abstract.__qualname__}"
        return abstract

    @staticmethod
    def class_to_name(abstract: str | type) -> str:
        """
        Get the simple name of a class.

        Args:
            abstract: Abstract type identifier or class.

        Returns:
            Simple class name without module or qualification.
        """
        if isinstance(abstract, type):
            return abstract.__name__
        return abstract

    @staticmethod
    def snake_case(value: str) -> str:
        """
        Convert a string to snake_case format.

        Args:
            value: The string to convert.

        Returns:
            The string in snake_case format (lowercase with underscores).

        Usage: `Str.snake_case("StartNode")` -> "start_node"
        Usage: `Str.snake_case("MyClassName")` -> "my_class_name"
        """
        # Insert an underscore before any uppercase letter that follows a lowercase letter
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
        # Insert an underscore before any uppercase letter that follows a lowercase or uppercase  letter
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)

        # TODO: this should be macroable
        # Convert to lowercase
        return s2.lower()

    @staticmethod
    def lower(value: str) -> str:
        """ """
        return value.lower()

    @staticmethod
    def class_to_snake_case(abstract: str | type) -> str:
        """
        Convert a Type to snake_case string suitable for graph node names.

        Args:
            abstract: Abstract type identifier or class.

        Returns:
            Snake_case string representation of the class name.

        Usage: `Str.to_node_name(StartNode)` -> "start_node"
        Usage: `Str.to_node_name("MyClassName")` -> "my_class_name"
        """
        name = Str.class_to_name(abstract)
        snake = Str.snake_case(name)
        return Str.lower(snake)

    @staticmethod
    def is_pattern(pattern: str | list[str], value: str, ignore_case: bool = False) -> bool:
        """
        Determine if a given string matches a given pattern.

        Args:
            pattern: Pattern(s) to match against (supports wildcards with *).
            value: The string value to check.
            ignore_case: Whether to ignore case when matching.

        Returns:
            True if value matches any pattern, False otherwise.
        """

        value = str(value)

        if not isinstance(pattern, list):
            pattern = [pattern]

        for p in pattern:
            p = str(p)

            # If the given value is an exact match we can of course return true right
            # from the beginning. Otherwise, we will translate asterisks and do an
            # actual pattern match against the two strings to see if they match.
            if p == "*" or p == value:
                return True

            if ignore_case and p.lower() == value.lower():
                return True

            # Escape special regex characters except asterisks
            p = re.escape(p)

            # Asterisks are translated into zero-or-more regular expression wildcards
            # to make it convenient to check if the strings starts with the given
            # pattern such as "library/*", making any string check convenient.
            p = p.replace(r"\*", ".*")

            flags = re.IGNORECASE | re.DOTALL if ignore_case else re.DOTALL
            if re.match(f"^{p}\\Z", value, flags):
                return True

        return False

    @staticmethod
    def slugify(text: str, separator: str = "-") -> str:
        """Convert a string to a URL-safe slug format.

        Converts text to lowercase, replaces non-alphanumeric characters with
        the specified separator, and removes leading/trailing separators.

        Args:
            text: The string to convert to a slug.
            separator: The separator to use (default: "-").

        Returns:
            The slugified string.

        Usage: `Str.slugify("Hello World")` -> "hello-world"
        Usage: `Str.slugify("Hello World", "_")` -> "hello_world"
        """
        import re

        # Convert to lowercase
        text = text.lower()
        # Replace non-alphanumeric characters with separator
        text = re.sub(r"[^a-z0-9]+", separator, text)
        # Remove leading/trailing separators
        text = text.strip(separator)
        return text
