"""Test suite for CommandRegistry."""

from __future__ import annotations

from argparse import Namespace
from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture

from byte.cli import ByteArgumentParser, Command, CommandRegistry

if TYPE_CHECKING:
    from byte import Application


class FakeTestCommand(Command):
    """Test command for registry tests."""

    @property
    def name(self) -> str:
        return "test"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog="test",
            description="Test command for registry",
        )
        parser.add_argument("arg", nargs="?", help="Test argument")
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        pass


@pytest.fixture
def providers():
    """Provide CLIServiceProvider for command registry tests."""
    from byte.cli import CLIServiceProvider

    return [CLIServiceProvider]


@pytest.mark.asyncio
async def test_register_and_get_slash_command(application: Application):
    """Test that slash commands can be registered and retrieved."""
    registry = application.make(CommandRegistry)
    command = FakeTestCommand(app=application)

    registry.register_slash_command(command)

    retrieved = registry.get_slash_command("test")
    assert retrieved is not None
    assert retrieved.name == "test"


@pytest.mark.asyncio
async def test_get_nonexistent_slash_command_returns_none(application: Application):
    """Test that getting a nonexistent slash command returns None."""
    registry = application.make(CommandRegistry)

    retrieved = registry.get_slash_command("nonexistent")
    assert retrieved is None


@pytest.mark.asyncio
async def test_get_slash_completions_with_no_slash_returns_empty(application: Application):
    """Test that completions without slash prefix return empty list."""
    registry = application.make(CommandRegistry)
    command = FakeTestCommand(app=application)
    registry.register_slash_command(command)

    completions = await registry.get_slash_completions("test")
    assert completions == []


@pytest.mark.asyncio
async def test_get_slash_completions_command_name_only(application: Application):
    """Test that partial command names return matching commands."""
    registry = application.make(CommandRegistry)
    command = FakeTestCommand(app=application)
    registry.register_slash_command(command)

    completions = await registry.get_slash_completions("/te")
    assert "test" in completions


@pytest.mark.asyncio
async def test_get_slash_completions_delegates_to_command(application: Application, mocker: MockerFixture):
    """Test that completions after space delegate to command's get_completions."""
    registry = application.make(CommandRegistry)
    command = FakeTestCommand(app=application)
    mock_get_completions = mocker.AsyncMock(return_value=["file1.py", "file2.py"])
    command.get_completions = mock_get_completions
    registry.register_slash_command(command)

    completions = await registry.get_slash_completions("/test arg")
    assert completions == ["file1.py", "file2.py"]
    mock_get_completions.assert_called_once_with("arg")


@pytest.mark.asyncio
async def test_command_handle_with_valid_args(application: Application, mocker: MockerFixture):
    """Test that command handle parses and executes with valid arguments."""
    command = FakeTestCommand(app=application)
    mock_execute = mocker.AsyncMock()
    command.execute = mock_execute

    await command.handle("myarg")

    mock_execute.assert_called_once()
    args = mock_execute.call_args[0][0]
    assert args.arg == "myarg"


@pytest.mark.asyncio
async def test_command_handle_with_invalid_args(application: Application, mocker: MockerFixture):
    """Test that command handle shows error panel with invalid arguments."""
    command = FakeTestCommand(app=application)
    mock_execute = mocker.AsyncMock()
    command.execute = mock_execute

    # Create a parser that will fail on invalid args
    parser = ByteArgumentParser(prog="test", description="Test command")
    parser.add_argument("required_arg", help="Required argument")

    # Mock the parser property to return our custom parser
    mocker.patch.object(type(command), "parser", new_callable=mocker.PropertyMock, return_value=parser)

    # Mock console to capture error output
    mock_console = mocker.MagicMock()
    application.instance("console", mock_console)

    await command.handle("")  # No args when one is required

    # Should print error panel, not call execute
    mock_console.print_error_panel.assert_called_once()
    mock_execute.assert_not_called()


@pytest.mark.asyncio
async def test_command_handle_with_no_args(application: Application, mocker: MockerFixture):
    """Test that commands with optional args work without arguments."""
    command = FakeTestCommand(app=application)
    mock_execute = mocker.AsyncMock()
    command.execute = mock_execute

    await command.handle("")

    mock_execute.assert_called_once()
    args = mock_execute.call_args[0][0]
    assert args.arg is None
