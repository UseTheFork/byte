import asyncio
from pathlib import Path


class CommandRunner:
    """Command execution helper utilities."""

    @staticmethod
    async def run(*args: str, cwd: Path | str) -> str:
        """Execute a command asynchronously and return its stdout.

        Args:
            *args: Command and arguments to execute.
            cwd: Working directory to execute the command in.

        Returns:
            The command's stdout as a decoded UTF-8 string.

        Raises:
            RuntimeError: If the command exits with a non-zero code, including stderr in the message.

        Usage: `output = await CommandRunner.run("git", "grep", "pattern", cwd="/path/to/repo")`
        """
        process = await asyncio.create_subprocess_exec(
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            stderr_str = stderr.decode("utf-8")
            stdout_str = stdout.decode("utf-8")
            error_detail = stderr_str or stdout_str or "(no error output)"
            raise RuntimeError(f"Command failed with exit code {process.returncode}: {error_detail}")

        return stdout.decode("utf-8")
