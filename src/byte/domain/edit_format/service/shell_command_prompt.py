from textwrap import dedent

shell_command_system = dedent("""
    # *Shell Command Block* Rules:
    Use *Shell Command blocks* to execute shell commands AFTER file edits are applied.

    ## Block Format:

    ```sh
    command to execute
    ```
    Or:
    ```bash
    command to execute
    second command to execute
    ```

    ## **CRITICAL RULES:**

    When to Use:
    - Use for operations that CANNOT be done via SEARCH/REPLACE blocks
    - Common: running tests, installing packages, git operations, building projects
    - Never edit files with shell commands (echo, sed, >>) - use SEARCH/REPLACE instead

    Safety:
    - Commands require user confirmation before execution
    - Dangerous operations prompt for explicit approval

    Execution:
    - Execute AFTER all SEARCH/REPLACE blocks succeed
    - Execute sequentially in order they appear
    - If file edits fail, shell commands are skipped

    Working Directory:
    - Commands run from project root
    - Use `cd` or `&&` to chain commands if needed""")


shell_practice_messages = [
    (
        "user",
        "Update the calculator and run the tests",
    ),
    (
        "assistant",
        dedent("""
        I'll update the calculator function and then run the test suite:

        ```python
        +++++++ calculator.py
        <<<<<<< SEARCH
        def add(a, b):
            return a + b
        =======
        def add(a: int, b: int) -> int:
            \"\"\"Add two integers and return the result.\"\"\"
            return a + b
        >>>>>>> REPLACE
        ```

        Now let's verify the changes:
        ```sh
        pytest tests/test_calculator.py -v
        ```"""),
    ),
    (
        "user",
        "Create a new config file and install the dependencies",
    ),
    (
        "assistant",
        dedent("""
        I'll create the config file and then install dependencies:
        ```python
        +++++++ config.py
        <<<<<<< SEARCH
        =======
        import os
        from dataclasses import dataclass

        @dataclass
        class Config:
            debug: bool = False
            port: int = 8000
        >>>>>>> REPLACE
        ```

        Now installing dependencies:
        ```bash
        uv sync
        ```"""),
    ),
]
