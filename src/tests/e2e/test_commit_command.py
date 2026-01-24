from __future__ import annotations

import io
from io import StringIO
from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture
from rich.console import Console as RichConsole
from rich.theme import Theme

from byte.cli import ByteTheme, ThemeRegistry
from byte.foundation import Console
from byte.git import CommitCommand
from byte.support.mixins import UserInteractive
from tests.utils import create_test_file

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """e2e tests get all providers"""
    from byte.main import PROVIDERS

    return PROVIDERS


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
    capture_console = RichConsole(file=string_io, theme=byte_theme)

    console = application.make(Console)
    console._console = capture_console

    return string_io


@pytest.mark.asyncio
async def test_commit_command_with_no_changes(
    application: Application,
    captured_console: StringIO,
    mocker: MockerFixture,
):
    """Test that commit command handles no changes gracefully."""

    # Mock user confirmation to return True
    mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)

    commit_command = application.make(CommitCommand)
    await commit_command.handle("")

    output = captured_console.getvalue()

    # Verify warning message is displayed
    assert "No staged changes to commit" in output


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_commit_command_stages_and_commits_untracked_files(
    application: Application,
    captured_console: StringIO,
    mocker: MockerFixture,
):
    """Test that Commit Agent generates a structured commit message."""

    # Mock user confirmation to return True
    mocker.patch.object(UserInteractive, "prompt_for_select", return_value="Single Commit")
    mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)
    mocker.patch.object(UserInteractive, "prompt_for_confirm_or_input", return_value=(True, ""))

    # Create and stage test files
    await create_test_file(application, "test_commit.txt", "test content")

    old_api_content = """
def get_users():
'''Old API endpoint'''
pass
"""
    await create_test_file(application, "old_api.py", old_api_content)

    new_api_content = """
def get_users_v2():
'''New API endpoint'''
return {'users': []}
"""
    await create_test_file(application, "new_api.py", new_api_content)

    commit_command = application.make(CommitCommand)
    await commit_command.handle("")

    # application["log"].info(captured_console.getvalue())

    output = captured_console.getvalue()

    # Verify staging messages
    assert output.count("Found 0 unstaged changes and 3 untracked changes") == 1
    assert output.count("Added 3 changes to commit") == 1

    # Verify agent execution messages
    assert output.count("Thinking...") == 1
    assert output.count("Using Tool...") == 1

    # Verify commit message contains expected content
    assert "chore: add initial project files" in output


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_commit_command_with_commit_plan(
    application: Application,
    captured_console: StringIO,
    mocker: MockerFixture,
):
    """Test that Commit Plan Agent generates multiple structured commits."""

    # Mock user confirmation to return True
    mocker.patch.object(UserInteractive, "prompt_for_select", return_value="Commit Plan")
    mocker.patch.object(UserInteractive, "prompt_for_confirmation", return_value=True)
    mocker.patch.object(UserInteractive, "prompt_for_confirm_or_input", return_value=(True, ""))

    # Create and stage test files
    await create_test_file(application, "test_commit.txt", "test content")

    old_api_content = """
def get_users():
'''Old API endpoint'''
pass
"""
    await create_test_file(application, "old_api.py", old_api_content)

    new_api_content = """
def get_users_v2():
'''New API endpoint'''
return {'users': []}
"""
    await create_test_file(application, "new_api.py", new_api_content)

    commit_command = application.make(CommitCommand)
    await commit_command.handle("")

    output = captured_console.getvalue()

    # Verify staging messages
    assert output.count("Found 0 unstaged changes and 3 untracked changes") == 1
    assert output.count("Added 3 changes to commit") == 1

    # Verify agent execution messages
    assert output.count("Thinking...") == 1
    assert output.count("Using Tool...") == 1

    # Verify commit message contains expected content
    assert "chore: add initial project files" in output
