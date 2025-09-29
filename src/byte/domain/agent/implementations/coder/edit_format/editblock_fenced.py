import re
from textwrap import dedent
from typing import List

from byte.domain.agent.implementations.coder.edit_format.base import (
    EditFormat,
    EditFormatPrompts,
    SearchReplaceBlock,
)
from byte.domain.agent.implementations.coder.edit_format.exceptions import (
    PreFlightCheckError,
)

# Credits to: https://github.com/Aider-AI/aider/blob/e4fc2f515d9ed76b14b79a4b02740cf54d5a0c0b/aider/coders/editblock_fenced_prompts.py
edit_format_system = dedent("""
    # *SEARCH/REPLACE block* Rules:

    Use *SEARCH/REPLACE blocks* to make precise edits to files. Each block specifies:
    - **What file** to modify (with full path)
    - **What content** to find (SEARCH section)
    - **What to replace** it with (REPLACE section)

    ## Block Format:

    Every *SEARCH/REPLACE block* must use this exact format:
    1. Opening fence with language: ```python
    2. Operation type and file path: `+++` or `---` followed by the *FULL* file path
    3. Search marker: <<<<<<< SEARCH
    4. Content to find (can be empty)
    5. Divider: =======
    6. Content to replace with (can be empty)
    7. Replace marker: >>>>>>> REPLACE
    8. Closing fence: ```

    ## Operation Types:
    - `+++` for **editing** existing files or **creating** new files
    - `---` for **removing** files or **replacing entire file contents**

    ## Examples:

    **Create a new file:**
    ```python
    +++ mathweb/flask/app.py
    <<<<<<< SEARCH
    =======
    import math
    from flask import Flask
    >>>>>>> REPLACE
    ```

    **Edit existing file content:**
    ```python
    +++ mathweb/flask/app.py
    <<<<<<< SEARCH
    from flask import Flask
    =======
    import math
    from flask import Flask
    >>>>>>> REPLACE
    ```

   **Remove entire file:**
    ```python
    --- mathweb/flask/app.py
    <<<<<<< SEARCH
    =======
    >>>>>>> REPLACE
    ```

    **Replace all file contents:**
    ```python
    --- mathweb/flask/app.py
    <<<<<<< SEARCH
    =======
    import math
    from flask import Flask
    >>>>>>> REPLACE
    ```

    ## **CRITICAL RULES:**

    File Paths:
    - Use the FULL file path exactly as shown by the user
    - No bold asterisks, quotes, or escaping around the path

    Search Content:
    - Must EXACTLY MATCH existing file content, character for character
    - Include all comments, docstrings, whitespace, etc.
    - If file contains wrapped/escaped content, match the literal file contents

    Block Strategy:
    - Keep blocks small and focused
    - Use multiple blocks for multiple changes to the same file
    - Include enough context lines to make each search unique
    - Only replace the first occurrence found

    File Operations:
    - Only edit files that the user has added to the chat
    - For new files: use +++ with empty SEARCH, content in REPLACE
    - To move code: use 2 blocks (1 to delete, 1 to insert)
    - To rename files: use shell commands after your response

    User Intent:
    - If user says "ok", "go ahead", or "do that" → provide SEARCH/REPLACE blocks
    - Wait for user confirmation before assuming edits are applied
    - ONLY EVER RETURN CODE IN A SEARCH/REPLACE BLOCK!""")

# {quad_backtick_reminder}

practice_messages = [
    (
        "user",
        """Before we start lets first practice the *SEARCH/REPLACE block* format.

        Change get_factorial() to use math.factorial""",
    ),
    (
        "assistant",
        dedent("""
        To make this change we need to modify `mathweb/flask/app.py` to:

        1. Import the math package.
        2. Remove the existing factorial() function.
        3. Update get_factorial() to call math.factorial instead.

        Here are the *SEARCH/REPLACE* blocks:

        ```python
        +++ mathweb/flask/app.py
        <<<<<<< SEARCH
        from flask import Flask
        =======
        import math
        from flask import Flask
        >>>>>>> REPLACE
        ```

        ```python
        +++ mathweb/flask/app.py
        <<<<<<< SEARCH
        def factorial(n):
            "compute factorial"

            if n == 0:
                return 1
            else:
                return n * factorial(n-1)

        =======
        >>>>>>> REPLACE
        ```

        ```python
        +++ mathweb/flask/app.py
        <<<<<<< SEARCH
            return str(factorial(n))
        =======
            return str(math.factorial(n))
        >>>>>>> REPLACE
        ```"""),
    ),
    (
        "user",
        dedent("""
        Refactor hello() into its own file."""),
    ),
    (
        "assistant",
        dedent("""
        To make this change we need to modify `main.py` and make a new file `hello.py`:

        1. Make a new hello.py file with hello() in it.
        2. Remove hello() from main.py and replace it with an import.

        Here are the *SEARCH/REPLACE* blocks:

        ```python
        +++ hello.py
        <<<<<<< SEARCH
        =======
        def hello():
            "print a greeting"

            print("hello")
        >>>>>>> REPLACE
        ```

        ```python
        +++ main.py
        <<<<<<< SEARCH
        def hello():
            "print a greeting"

            print("hello")
        =======
        from hello import hello
        >>>>>>> REPLACE
        ```"""),
    ),
    ("user", "Remove the old_config.py file that's no longer needed."),
    (
        "assistant",
        dedent("""
        To remove this file we need to delete `old_config.py`:

        1. Remove the old_config.py file completely from the project.

        Here is the *SEARCH/REPLACE* block:

        ```python
        --- old_config.py
        <<<<<<< SEARCH
        =======
        >>>>>>> REPLACE
        ```"""),
    ),
    (
        "user",
        "Replace all the contents of config.py with a new configuration structure.",
    ),
    (
        "assistant",
        dedent("""
        To replace all the contents we need to completely rewrite `config.py`:

        1. Replace the entire contents of config.py with the new configuration structure.

        Here is the *SEARCH/REPLACE* block:

        ```python
        --- config.py
        <<<<<<< SEARCH
        =======
        import os
        from dataclasses import dataclass

        @dataclass
        class AppConfig:
            debug: bool = False
            port: int = 8000
            database_url: str = os.getenv("DATABASE_URL", "sqlite:///app.db")
        >>>>>>> REPLACE
        ```"""),
    ),
    (
        "user",
        "Add error handling to the calculator function and update the docstring.",
    ),
    (
        "assistant",
        dedent("""
        To add error handling we need to modify `calculator.py` in two places:

        1. Update the docstring to mention error handling.
        2. Add try-catch block around the calculation.

        Here are the *SEARCH/REPLACE* blocks:

        ```python
        +++ calculator.py
        <<<<<<< SEARCH
        def calculate(a, b):
            "Simple calculator function"
        =======
        def calculate(a, b):
            "Simple calculator function with error handling"
        >>>>>>> REPLACE
        ```

        ```python
        +++ calculator.py
        <<<<<<< SEARCH
            return a / b
        =======
            try:
                return a / b
            except ZeroDivisionError:
                return "Error: Cannot divide by zero"
        >>>>>>> REPLACE
        ```"""),
    ),
]


class BlockedFenceEditFormat(EditFormat):
    add_file_marker: str = "+++"
    remove_file_marker: str = "---"
    search: str = "<<<<<<< SEARCH"
    divider: str = "======="
    replace: str = ">>>>>>> REPLACE"

    async def boot(self):
        await super().boot()
        self.prompts = EditFormatPrompts(
            system=edit_format_system, examples=practice_messages
        )

    def parse_content_to_blocks(self, content: str) -> List[SearchReplaceBlock]:
        """Extract SEARCH/REPLACE blocks from AI response content."""

        blocks = []

        # Pattern to match the entire SEARCH/REPLACE block structure
        pattern = r"```\w*\n(\+\+\+|---) (.+?)\n<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE\n```"

        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            file_path, search_content, replace_content = match
            blocks.append(
                SearchReplaceBlock(
                    file_path=file_path.strip(),
                    search_content=search_content,
                    replace_content=replace_content,
                )
            )
        return blocks

    def pre_flight_check(self, content: str) -> None:
        """Validate that SEARCH/REPLACE block markers are properly balanced.

        Counts occurrences of all five required markers and raises an exception
        if they don't match, indicating malformed blocks.
        """
        search_count = content.count(self.search)
        replace_count = content.count(self.replace)
        divider_count = content.count(self.divider)
        file_marker_count = content.count(self.add_file_marker) + content.count(
            self.remove_file_marker
        )

        if not (search_count == replace_count == divider_count == file_marker_count):
            raise PreFlightCheckError(
                f"Malformed SEARCH/REPLACE blocks: "
                f"SEARCH={search_count}, REPLACE={replace_count}, "
                f"dividers={divider_count}, file markers={file_marker_count}. "
                f"All counts must be equal."
            )
