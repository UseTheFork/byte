from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from byte.foundation import Application as PrimaryApplication


class Application:
    """Console application for handling command execution."""

    bootstrappers: list = []

    def __init__(self, byte: PrimaryApplication):
        """
        Initialize the console application.

        Args:
            byte: The application container instance.
        """
        self.byte = byte

        self.bootstrap()

    def bootstrap(self) -> None:
        """
        Bootstrap the console application.

        Returns:
            None
        """
        for bootstrapper in self.bootstrappers:
            bootstrapper(self)

    async def call(
        self,
        command: str,
        parameters: dict[str, Any] = {},
        output_buffer: Any | None = None,
    ) -> int:
        """
        Run a console command by name.

        Args:
            command: The command name to run.
            parameters: Parameters to pass to the command.
            output_buffer: Optional output buffer for capturing command output.

        Returns:
            Exit status code (0 for success, non-zero for error).
        """

        # try:
        # Resolve the command from container

        return 0
        # except Exception as e:
        #     self._output = f"Error executing command: {e!s}"
        #     return 1

    async def run(self, input: list[str]) -> int:
        """
        Run the console application with command line arguments.

        Returns:
            Exit status code.
        """
        args = input[1:]

        command_name = args[0]
        remaining_args = args[1:]
        print(1234)
        print(1234)
        print(1234)

        return await self.call(command_name)

    def terminate(self) -> None:
        pass

    def get_byte(self) -> PrimaryApplication:
        """
        Get the Byte application instance.

        Returns:
            Byte Application instance.
        """
        return self.byte

    @classmethod
    def starting(cls, callback):
        """
        Register a console "starting" bootstrapper.

        Args:
            callback: Callable that takes the application instance.
        """
        cls.bootstrappers.append(callback)
