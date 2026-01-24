from __future__ import annotations

import io
from io import StringIO
from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture
from rich.console import Console as RichConsole
from rich.theme import Theme

from byte.agent import AskAgent
from byte.agent.implementations.conventions.constants import FOCUS_MESSAGES
from byte.cli import ByteTheme, CLIServiceProvider, ThemeRegistry
from byte.foundation import Console
from byte.support.mixins import UserInteractive
from tests.utils import create_test_file

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide service providers for coder agent tests."""
    from byte.agent import AgentServiceProvider
    from byte.files import FileServiceProvider

    return [AgentServiceProvider, FileServiceProvider, CLIServiceProvider]


@pytest.fixture
def captured_console(
    application: Application,
    mocker: MockerFixture,
):
    theme_registry = ThemeRegistry()
    selected_theme: ByteTheme = theme_registry.get_theme("mocha")

    # Apply Base16 colors to semantic style names.
    byte_theme = Theme(
        {
            "text": selected_theme.base05,  # Default Foreground
            "success": selected_theme.base0B,  # Green - Strings, Inserted
            "error": selected_theme.base08,  # Red - Variables, Tags
            "warning": selected_theme.base0A,  # Yellow - Classes, Bold
            "info": selected_theme.base0C,  # Teal - Support, Regex
            "danger": selected_theme.base08,  # Red - Variables, Tags
            "primary": selected_theme.base0D,  # Blue - Functions, Headings
            "secondary": selected_theme.base0E,  # Mauve - Keywords, Italic
            "muted": selected_theme.base03,  # Comments, Invisibles
            "subtle": selected_theme.base04,  # Dark Foreground
            "active_border": selected_theme.base07,  # Light Background
            "inactive_border": selected_theme.base03,  # Comments, Invisibles
        }
    )

    string_io = io.StringIO()
    console = RichConsole(file=string_io, theme=byte_theme)

    mocker.patch.object(Console, "console", console)
    mocker.patch.object(application["console"], "console", console)

    return string_io


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_silent_mode_produces_no_console_output(
    application: Application,
    mocker: MockerFixture,
    captured_console: StringIO,
):
    """Test that agent execution in silent mode produces no console output."""

    # Create the agent
    agent = application.make(AskAgent)

    # Request to create a new file
    request = "Create a new file called hello.py with a simple hello world function"

    await agent.execute(request, display_mode="silent")

    captured_output = captured_console.getvalue()

    assert captured_output == ""


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_thinking_mode_produces_spinner_console_output(
    application: Application,
    mocker: MockerFixture,
    captured_console: StringIO,
):
    """Test that agent execution in thinking mode produces no console output."""

    # Create the agent
    agent = application.make(AskAgent)

    # Request to create a new file
    request = "Create a new file called hello.py with a simple hello world function"

    await agent.execute(request, display_mode="thinking")

    captured_output = captured_console.getvalue()

    assert "Thinking..." in captured_output
    assert "Ask Agent" not in captured_output


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_verbose_mode_produces_all_console_output(
    application: Application,
    mocker: MockerFixture,
    captured_console: StringIO,
):
    """Test that agent execution in verbose mode produces full console output including spinner and agent name."""

    # Create the agent
    agent = application.make(AskAgent)

    # Request to create a new file
    request = "Create a new file called hello.py with a simple hello world function"

    await agent.execute(request, display_mode="verbose")

    captured_output = captured_console.getvalue()

    # application["log"].info(captured_output)

    assert captured_output.count("Thinking...") == 1
    assert captured_output.count("Ask Agent") == 1


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_verbose_mode_shows_tool_calls(
    application: Application,
    mocker: MockerFixture,
    captured_console: StringIO,
):
    """Test that agent execution in verbose mode displays tool call information."""
    from byte.agent import ConventionAgent

    mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

    focus = FOCUS_MESSAGES.get("Comment Standards")

    # Create test files with various comment styles
    python_content = """def calculate(a, b):
# This is a comment
return a + b

class MyClass:
'''This is a docstring'''
pass
"""
    await create_test_file(application, "example.py", python_content)

    javascript_content = """// This is a single-line comment
function greet(name) {
/* This is a
    multi-line comment */
return `Hello, ${name}`;
}
"""
    await create_test_file(application, "example.js", javascript_content)

    # Create the agent
    agent = application.make(ConventionAgent)

    await agent.execute(focus.focus_message, display_mode="verbose")

    # application["log"].info(result.keys())

    captured_output = captured_console.getvalue()

    assert captured_output.count("Using Tool") == 1
    assert captured_output.count("Convention Agent") == 2
    assert "Tool Result" in captured_output
