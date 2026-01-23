"""Test suite for Subprocess Agent."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from byte.prompt_format import Boundary, BoundaryType
from byte.support.mixins import UserInteractive

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide AgentServiceProvider for subprocess agent tests."""
    from byte.agent import AgentServiceProvider

    return [AgentServiceProvider]


@pytest.mark.asyncio
async def test_subprocess_agent_executes_command(application: Application, mocker):
    """Test that Subprocess Agent executes a command and returns results."""

    from byte.agent.implementations.subprocess.agent import SubprocessAgent

    # Create the agent
    agent = application.make(SubprocessAgent)

    mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

    result = await agent.execute("echo 'hello world'", display_mode="silent")

    # Verify the command was executed and added to history
    assert "history_messages" in result
    assert len(result["history_messages"]) == 1
    assert Boundary.open(BoundaryType.STDOUT) in result["history_messages"][0].content
    assert Boundary.open(BoundaryType.STDERR) not in result["history_messages"][0].content
    assert "subprocess execution" in result["history_messages"][0].content


@pytest.mark.asyncio
async def test_subprocess_agent_user_declines_adding_output(application: Application, mocker):
    """Test that Subprocess Agent respects user declining to add output to context."""

    from byte.agent.implementations.subprocess.agent import SubprocessAgent

    # Create the agent
    agent = application.make(SubprocessAgent)

    mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=False)

    result = await agent.execute("echo 'test output'", display_mode="silent")

    # Verify the command was executed but output was not added to history
    assert "history_messages" in result
    assert len(result["history_messages"]) == 0
    assert "scratch_messages" in result
    assert len(result["scratch_messages"]) == 0


@pytest.mark.asyncio
async def test_subprocess_agent_command_with_stderr(application: Application, mocker):
    """Test that Subprocess Agent captures stderr output when command fails."""

    from byte.agent.implementations.subprocess.agent import SubprocessAgent

    # Create the agent
    agent = application.make(SubprocessAgent)

    mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

    # Run a command that writes to stderr
    result = await agent.execute("ls /nonexistent_directory", display_mode="silent")

    # Verify stderr was captured
    assert "history_messages" in result
    assert len(result["history_messages"]) == 1
    assert Boundary.open(BoundaryType.STDERR) in result["history_messages"][0].content
    assert "subprocess execution" in result["history_messages"][0].content


@pytest.mark.asyncio
async def test_subprocess_agent_command_with_exit_code(application: Application, mocker):
    """Test that Subprocess Agent captures non-zero exit codes."""

    from byte.agent.implementations.subprocess.agent import SubprocessAgent

    # Create the agent
    agent = application.make(SubprocessAgent)

    mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

    # Run a command that exits with non-zero status
    result = await agent.execute("false", display_mode="silent")

    # Verify exit code was captured in metadata
    assert "history_messages" in result
    assert len(result["history_messages"]) == 1
    assert 'exit_code="1"' in result["history_messages"][0].content
    assert "subprocess execution" in result["history_messages"][0].content


@pytest.mark.asyncio
async def test_subprocess_agent_multiple_commands_in_sequence(application: Application, mocker):
    """Test that Subprocess Agent can execute multiple commands in sequence."""

    from byte.agent.implementations.subprocess.agent import SubprocessAgent

    # Create the agent
    agent = application.make(SubprocessAgent)

    mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

    # Execute first command
    result1 = await agent.execute("echo 'first'", display_mode="silent")

    # Execute second command
    result2 = await agent.execute("echo 'second'", display_mode="silent")

    # Verify both commands were executed and added to history
    assert len(result1["history_messages"]) == 1
    assert "first" in result1["history_messages"][0].content

    assert len(result2["history_messages"]) == 1
    assert "second" in result2["history_messages"][0].content


@pytest.mark.asyncio
async def test_subprocess_agent_metadata_attributes_in_context(application: Application, mocker):
    """Test that Subprocess Agent includes correct metadata attributes in context block."""

    from byte.agent.implementations.subprocess.agent import SubprocessAgent

    # Create the agent
    agent = application.make(SubprocessAgent)

    mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

    # Execute a command
    result = await agent.execute("echo 'test'", display_mode="silent")

    # Verify metadata attributes are present in the context block
    assert len(result["history_messages"]) == 1
    message_content = result["history_messages"][0].content

    # Check for subprocess execution context with metadata
    assert 'type="subprocess execution"' in message_content
    assert "command=\"echo 'test'\"" in message_content
    assert 'exit_code="0"' in message_content
