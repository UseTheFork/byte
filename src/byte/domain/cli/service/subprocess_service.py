import asyncio
from typing import Optional

from byte.core.config.config import ByteConfg
from byte.core.service.base_service import Service
from byte.domain.cli.schemas import SubprocessResult


class SubprocessService(Service):
    """Service for executing subprocess commands with async support.

    Provides a clean interface for running shell commands asynchronously and
    capturing their output, exit codes, and errors in a structured format.

    Usage: `result = await subprocess_service.run("ls -la")` -> execute command
    """

    async def run(
        self,
        command: str,
        timeout: Optional[float] = None,
    ) -> SubprocessResult:
        """Execute a shell command and return structured results.

        Always runs commands from the project root directory.

        Args:
                command: Shell command to execute
                timeout: Optional timeout in seconds

        Returns:
                SubprocessResult with exit code, stdout, stderr, and metadata

        Usage: `result = await service.run("echo hello")`
        Usage: `result = await service.run("pytest", timeout=30.0)`
        """
        try:
            # Get project root from config
            config = await self.make(ByteConfg)
            working_dir = str(config.project_root)

            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
            )

            # Run with optional timeout
            if timeout:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            else:
                stdout, stderr = await process.communicate()

            exit_code = process.returncode

            return SubprocessResult(
                exit_code=exit_code if exit_code is not None else -1,
                stdout=stdout.decode("utf-8", errors="ignore"),
                stderr=stderr.decode("utf-8", errors="ignore"),
                command=command,
                cwd=working_dir,
            )

        except TimeoutError:
            # Handle timeout
            return SubprocessResult(
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                command=command,
                cwd=working_dir,
            )

        except Exception as e:
            # Handle other execution errors
            return SubprocessResult(
                exit_code=-1,
                stdout="",
                stderr=f"Error executing command: {e!s}",
                command=command,
                cwd=working_dir,
            )
