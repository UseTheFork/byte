import datetime
from collections.abc import Iterable
from pathlib import Path

from byte.support import Service


class PromptHistoryService(Service):
    """ """

    """
    :class:`.History` class that stores all strings in a file.
    """

    def boot(self) -> None:
        self.filename = self.app.cache_path(".input_history")
        # In memory storage for strings.
        self._loaded = False

        # History that's loaded already, in reverse order. Latest, most recent
        # item first.
        self._loaded_strings: list[str] = []

    async def load(self) -> None:
        """
        Load the history and yield all the entries in reverse order (latest,
        most recent history entry first).

        This method can be called multiple times from the `Buffer` to
        repopulate the history when prompting for a new input. So we are
        responsible here for both caching, and making sure that strings that
        were were appended to the history will be incorporated next time this
        method is called.
        """
        if not self._loaded:
            self._loaded_strings = list(self.load_history_strings())
            self._loaded = True

    def get_strings(self) -> list[str]:
        """
        Get the strings from the history that are loaded so far.
        (In order. Newest item first.)
        """
        return self._loaded_strings
        # return self._loaded_strings[::-1]

    def append_string(self, string: str) -> None:
        "Add string to the history."
        self._loaded_strings.insert(0, string)
        self.store_string(string)

    def load_history_strings(self) -> Iterable[str]:
        strings: list[str] = []
        lines: list[str] = []

        def add() -> None:
            if lines:
                # Join and drop trailing newline.
                string = "".join(lines)[:-1]

                strings.append(string)

        if Path(self.filename).exists():
            with open(self.filename, "rb") as f:
                for line_bytes in f:
                    line = line_bytes.decode("utf-8", errors="replace")

                    if line.startswith("+"):
                        lines.append(line[1:])
                    else:
                        add()
                        lines = []

                add()

        # Reverse the order, because newest items have to go first.
        return reversed(strings)

    def store_string(self, string: str) -> None:
        # Save to file.
        with open(self.filename, "ab") as f:

            def write(t: str) -> None:
                f.write(t.encode("utf-8"))

            write(f"\n# {datetime.datetime.now()}\n")
            for line in string.split("\n"):
                write(f"+{line}\n")
