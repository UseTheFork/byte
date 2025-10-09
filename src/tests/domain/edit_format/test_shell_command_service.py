"""Comprehensive test suite for ShellCommandService.

Tests the complete lifecycle of shell command operations including parsing,
validation, and execution of shell command blocks.
"""

from pathlib import Path
from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest

from byte.domain.edit_format.models import BlockStatus, ShellCommandBlock
from byte.domain.edit_format.service.shell_command_service import ShellCommandService


class TestShellCommandServiceParsing:
    """Test suite for parsing shell command blocks from content."""

    @pytest.mark.asyncio
    async def test_parse_single_sh_block(
        self, shell_command_service: ShellCommandService
    ):
        """Test parsing a single shell command block with 'sh' language."""
        content = dedent("""
        I'll run the tests:

        ```sh
        pytest tests/ -v
        ```
        """)

        blocks = shell_command_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].command == "pytest tests/ -v"
        assert blocks[0].block_status == BlockStatus.VALID

    @pytest.mark.asyncio
    async def test_parse_single_bash_block(
        self, shell_command_service: ShellCommandService
    ):
        """Test parsing a single shell command block with 'bash' language."""
        content = dedent("""
        I'll install dependencies:

        ```bash
        uv sync
        ```
        """)

        blocks = shell_command_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].command == "uv sync"
        assert blocks[0].block_status == BlockStatus.VALID

    @pytest.mark.asyncio
    async def test_parse_multiple_commands_single_block(
        self, shell_command_service: ShellCommandService
    ):
        """Test parsing multiple commands within a single block."""
        content = dedent("""
        I'll run several commands:

        ```bash
        uv sync
        pytest tests/
        ruff check .
        ```
        """)

        blocks = shell_command_service.parse_content_to_blocks(content)

        assert len(blocks) == 3
        assert blocks[0].command == "uv sync"
        assert blocks[1].command == "pytest tests/"
        assert blocks[2].command == "ruff check ."

    @pytest.mark.asyncio
    async def test_parse_multiple_blocks(
        self, shell_command_service: ShellCommandService
    ):
        """Test parsing multiple separate shell command blocks."""
        content = dedent("""
        First, install dependencies:

        ```sh
        uv sync
        ```

        Then run tests:

        ```bash
        pytest tests/ -v
        ```
        """)

        blocks = shell_command_service.parse_content_to_blocks(content)

        assert len(blocks) == 2
        assert blocks[0].command == "uv sync"
        assert blocks[1].command == "pytest tests/ -v"

    @pytest.mark.asyncio
    async def test_parse_no_blocks(self, shell_command_service: ShellCommandService):
        """Test parsing content with no shell command blocks."""
        content = "This is just some text without any command blocks."

        blocks = shell_command_service.parse_content_to_blocks(content)

        assert len(blocks) == 0

    @pytest.mark.asyncio
    async def test_parse_ignores_other_language_blocks(
        self, shell_command_service: ShellCommandService
    ):
        """Test that parser ignores code blocks with other languages."""
        content = dedent("""
        ```python
        print("hello")
        ```

        ```sh
        echo "test"
        ```

        ```javascript
        console.log("test")
        ```
        """)

        blocks = shell_command_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].command == 'echo "test"'

    @pytest.mark.asyncio
    async def test_parse_strips_whitespace(
        self, shell_command_service: ShellCommandService
    ):
        """Test that parser strips leading/trailing whitespace from commands."""
        content = dedent("""
        ```bash

        pytest tests/

        ruff check .

        ```
        """)

        blocks = shell_command_service.parse_content_to_blocks(content)

        assert len(blocks) == 2
        assert blocks[0].command == "pytest tests/"
        assert blocks[1].command == "ruff check ."

    @pytest.mark.asyncio
    async def test_parse_working_directory_set_from_config(
        self, shell_command_service: ShellCommandService, tmp_project_root: Path
    ):
        """Test that working directory is set from project root when available."""
        content = dedent("""
        ```sh
        ls -la
        ```
        """)

        blocks = shell_command_service.parse_content_to_blocks(content)

        assert len(blocks) == 1
        assert blocks[0].working_dir == str(tmp_project_root)


class TestShellCommandServiceExecution:
    """Test suite for executing shell command blocks."""

    @pytest.mark.asyncio
    async def test_execute_successful_command(
        self, shell_command_service: ShellCommandService, monkeypatch
    ):
        """Test successful execution of a shell command."""

        # Mock user confirmation
        async def mock_confirm(message, default):
            return True

        monkeypatch.setattr(
            shell_command_service, "prompt_for_confirmation", mock_confirm
        )

        # Mock subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            blocks = [
                ShellCommandBlock(
                    command="echo test",
                    working_dir="",
                    block_status=BlockStatus.VALID,
                )
            ]

            executed_blocks = await shell_command_service.execute_blocks(blocks)

            assert len(executed_blocks) == 1
            assert "Success" in executed_blocks[0].status_message
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_failed_command(
        self, shell_command_service: ShellCommandService, monkeypatch
    ):
        """Test execution of a command that fails."""

        # Mock user confirmation
        async def mock_confirm(message, default):
            return True

        monkeypatch.setattr(
            shell_command_service, "prompt_for_confirmation", mock_confirm
        )

        # Mock subprocess.run with failure
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error message"

        with patch("subprocess.run", return_value=mock_result):
            blocks = [
                ShellCommandBlock(
                    command="false",
                    working_dir="",
                    block_status=BlockStatus.VALID,
                )
            ]

            executed_blocks = await shell_command_service.execute_blocks(blocks)

            assert len(executed_blocks) == 1
            assert "Failed" in executed_blocks[0].status_message
            assert "Error message" in executed_blocks[0].status_message

    @pytest.mark.asyncio
    async def test_execute_user_cancels(
        self, shell_command_service: ShellCommandService, monkeypatch
    ):
        """Test that execution is skipped when user cancels confirmation."""

        # Mock user confirmation to return False
        async def mock_confirm(message, default):
            return False

        monkeypatch.setattr(
            shell_command_service, "prompt_for_confirmation", mock_confirm
        )

        blocks = [
            ShellCommandBlock(
                command="echo test",
                working_dir="",
                block_status=BlockStatus.VALID,
            )
        ]

        with patch("subprocess.run") as mock_run:
            executed_blocks = await shell_command_service.execute_blocks(blocks)

            assert len(executed_blocks) == 1
            assert "skipped by user" in executed_blocks[0].status_message
            mock_run.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_timeout(
        self, shell_command_service: ShellCommandService, monkeypatch
    ):
        """Test handling of command timeout."""

        # Mock user confirmation
        async def mock_confirm(message, default):
            return True

        monkeypatch.setattr(
            shell_command_service, "prompt_for_confirmation", mock_confirm
        )

        # Mock subprocess.run to raise TimeoutExpired
        with patch(
            "subprocess.run",
            side_effect=__import__("subprocess").TimeoutExpired("cmd", 300),
        ):
            blocks = [
                ShellCommandBlock(
                    command="sleep 1000",
                    working_dir="",
                    block_status=BlockStatus.VALID,
                )
            ]

            executed_blocks = await shell_command_service.execute_blocks(blocks)

            assert len(executed_blocks) == 1
            assert "timed out" in executed_blocks[0].status_message

    @pytest.mark.asyncio
    async def test_execute_subprocess_error(
        self, shell_command_service: ShellCommandService, monkeypatch
    ):
        """Test handling of subprocess errors."""

        # Mock user confirmation
        async def mock_confirm(message, default):
            return True

        monkeypatch.setattr(
            shell_command_service, "prompt_for_confirmation", mock_confirm
        )

        # Mock subprocess.run to raise OSError
        with patch("subprocess.run", side_effect=OSError("Command not found")):
            blocks = [
                ShellCommandBlock(
                    command="nonexistent_command",
                    working_dir="",
                    block_status=BlockStatus.VALID,
                )
            ]

            executed_blocks = await shell_command_service.execute_blocks(blocks)

            assert len(executed_blocks) == 1
            assert "Execution error" in executed_blocks[0].status_message

    @pytest.mark.asyncio
    async def test_execute_with_working_directory(
        self,
        shell_command_service: ShellCommandService,
        tmp_project_root: Path,
        monkeypatch,
    ):
        """Test that commands execute in the specified working directory."""

        # Mock user confirmation
        async def mock_confirm(message, default):
            return True

        monkeypatch.setattr(
            shell_command_service, "prompt_for_confirmation", mock_confirm
        )

        # Mock subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            blocks = [
                ShellCommandBlock(
                    command="pwd",
                    working_dir=str(tmp_project_root),
                    block_status=BlockStatus.VALID,
                )
            ]

            await shell_command_service.execute_blocks(blocks)

            # Verify subprocess.run was called with correct cwd
            call_args = mock_run.call_args
            assert call_args[1]["cwd"] == tmp_project_root

    @pytest.mark.asyncio
    async def test_execute_multiple_commands_sequentially(
        self, shell_command_service: ShellCommandService, monkeypatch
    ):
        """Test that multiple commands are executed in sequence."""

        # Mock user confirmation
        async def mock_confirm(message, default):
            return True

        monkeypatch.setattr(
            shell_command_service, "prompt_for_confirmation", mock_confirm
        )

        execution_order = []

        def mock_run(*args, **kwargs):
            execution_order.append(args[0])
            result = MagicMock()
            result.returncode = 0
            result.stdout = f"Executed {args[0]}"
            result.stderr = ""
            return result

        with patch("subprocess.run", side_effect=mock_run):
            blocks = [
                ShellCommandBlock(
                    command="first_command",
                    working_dir="",
                    block_status=BlockStatus.VALID,
                ),
                ShellCommandBlock(
                    command="second_command",
                    working_dir="",
                    block_status=BlockStatus.VALID,
                ),
                ShellCommandBlock(
                    command="third_command",
                    working_dir="",
                    block_status=BlockStatus.VALID,
                ),
            ]

            await shell_command_service.execute_blocks(blocks)

            assert execution_order == [
                "first_command",
                "second_command",
                "third_command",
            ]

    @pytest.mark.asyncio
    async def test_execute_skips_invalid_blocks(
        self, shell_command_service: ShellCommandService, monkeypatch
    ):
        """Test that invalid blocks are skipped during execution."""

        # Mock user confirmation
        async def mock_confirm(message, default):
            return True

        monkeypatch.setattr(
            shell_command_service, "prompt_for_confirmation", mock_confirm
        )

        with patch("subprocess.run") as mock_run:
            blocks = [
                ShellCommandBlock(
                    command="valid_command",
                    working_dir="",
                    block_status=BlockStatus.VALID,
                ),
                ShellCommandBlock(
                    command="invalid_command",
                    working_dir="",
                    block_status=BlockStatus.READ_ONLY_ERROR,  # Invalid status
                ),
            ]

            await shell_command_service.execute_blocks(blocks)

            # Only valid command should be executed
            assert mock_run.call_count == 1


class TestShellCommandServiceUtilities:
    """Test suite for utility methods."""

    @pytest.mark.asyncio
    async def test_remove_blocks_from_content_single_command(
        self, shell_command_service: ShellCommandService
    ):
        """Test removing shell command blocks with single command."""
        content = dedent("""
        I'll run the tests:

        ```sh
        pytest tests/ -v
        ```

        That should do it!
        """)

        cleaned = shell_command_service.remove_blocks_from_content(content)

        # Shell block fence should be removed
        assert "```sh" not in cleaned

        # Command should appear in summary message (in backticks), not as a code block
        assert "Executed command: `pytest tests/ -v`" in cleaned
        assert "That should do it!" in cleaned

    @pytest.mark.asyncio
    async def test_remove_blocks_from_content_multiple_commands(
        self, shell_command_service: ShellCommandService
    ):
        """Test removing shell command blocks with multiple commands."""
        content = dedent("""
        I'll run several commands:

        ```bash
        uv sync
        pytest tests/
        ruff check .
        ```

        Done!
        """)

        cleaned = shell_command_service.remove_blocks_from_content(content)

        assert "```bash" not in cleaned
        assert "uv sync" not in cleaned
        assert "Executed 3 commands" in cleaned
        assert "Done!" in cleaned

    @pytest.mark.asyncio
    async def test_remove_blocks_preserves_non_shell_blocks(
        self, shell_command_service: ShellCommandService
    ):
        """Test that non-shell code blocks are preserved."""
        content = dedent("""
        Here's some Python code:

        ```python
        def hello():
            print("Hello")
        ```

        And a shell command:

        ```sh
        echo "test"
        ```
        """)

        cleaned = shell_command_service.remove_blocks_from_content(content)

        # Python block should be preserved
        assert "```python" in cleaned
        assert "def hello():" in cleaned

        # Shell block fence should be removed
        assert "```sh" not in cleaned

        # Command should appear in summary message, not as a code block
        assert "Executed command" in cleaned
        assert '`echo "test"`' in cleaned  # Command in backticks in summary


class TestShellCommandServiceIntegration:
    """Integration tests for the complete shell command workflow."""

    @pytest.mark.asyncio
    async def test_handle_complete_workflow(
        self, shell_command_service: ShellCommandService, monkeypatch
    ):
        """Test complete workflow: parse, validate, and execute commands."""

        # Mock user confirmation
        async def mock_confirm(message, default):
            return True

        monkeypatch.setattr(
            shell_command_service, "prompt_for_confirmation", mock_confirm
        )

        # Mock subprocess.run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Test output"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            content = dedent("""
            I'll run the tests:

            ```sh
            pytest tests/ -v
            ```
            """)

            blocks = await shell_command_service.handle(content)

            assert len(blocks) == 1
            assert blocks[0].command == "pytest tests/ -v"
            assert blocks[0].block_status == BlockStatus.VALID
            assert "Success" in blocks[0].status_message

    @pytest.mark.asyncio
    async def test_handle_mixed_success_and_failure(
        self, shell_command_service: ShellCommandService, monkeypatch
    ):
        """Test handling content with commands that succeed and fail."""

        # Mock user confirmation
        async def mock_confirm(message, default):
            return True

        monkeypatch.setattr(
            shell_command_service, "prompt_for_confirmation", mock_confirm
        )

        # Mock subprocess.run to succeed for first call, fail for second
        call_count = 0

        def mock_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            result = MagicMock()
            if call_count == 1:
                result.returncode = 0
                result.stdout = "Success"
                result.stderr = ""
            else:
                result.returncode = 1
                result.stdout = ""
                result.stderr = "Error"
            return result

        with patch("subprocess.run", side_effect=mock_run):
            content = dedent("""
            ```bash
            echo "success"
            false
            ```
            """)

            blocks = await shell_command_service.handle(content)

            assert len(blocks) == 2
            assert "Success" in blocks[0].status_message
            assert "Failed" in blocks[1].status_message
