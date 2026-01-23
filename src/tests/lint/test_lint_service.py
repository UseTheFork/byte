"""Test suite for LintService."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def providers():
    """Provide LintServiceProvider for lint service tests."""
    from byte.git import GitServiceProvider
    from byte.lint import LintServiceProvider

    return [GitServiceProvider, LintServiceProvider]


@pytest.fixture
def config():
    """Create a ByteConfig instance with lint enabled."""
    from byte.config import ByteConfig
    from byte.lint.config import LintCommand

    config = ByteConfig()
    config.lint.enable = True
    config.lint.commands = [
        LintCommand(command=["echo", "linting"], languages=["python"]),
    ]
    return config


@pytest.mark.asyncio
async def test_validate_raises_when_linting_disabled(application: Application):
    """Test that validate raises LintConfigException when linting is disabled."""
    from byte.lint import LintConfigException, LintService

    # Disable linting
    application["config"].lint.enable = False

    service = application.make(LintService)

    with pytest.raises(LintConfigException, match="Linting is disabled"):
        await service.validate()


@pytest.mark.asyncio
async def test_validate_raises_when_no_commands_configured(application: Application):
    """Test that validate raises LintConfigException when no commands configured."""
    from byte.lint import LintConfigException, LintService

    # Enable linting but clear commands
    application["config"].lint.enable = True
    application["config"].lint.commands = []

    service = application.make(LintService)

    with pytest.raises(LintConfigException, match="No lint commands configured"):
        await service.validate()


@pytest.mark.asyncio
async def test_validate_returns_true_when_configured(application: Application):
    """Test that validate returns True when linting is properly configured."""
    from byte.lint import LintService

    service = application.make(LintService)
    result = await service.validate()

    assert result is True


@pytest.mark.asyncio
async def test_handle_calls_lint_changed_files(application: Application):
    """Test that handle calls lint_changed_files."""
    from unittest.mock import AsyncMock, patch

    from byte.lint import LintService

    service = application.make(LintService)

    with patch.object(service, "lint_changed_files", new_callable=AsyncMock) as mock_lint:
        mock_lint.return_value = []
        await service.handle()

        mock_lint.assert_called_once()


@pytest.mark.asyncio
async def test_lint_changed_files_filters_removed_files(application: Application):
    """Test that lint_changed_files filters out removed files."""

    from byte.git import GitService
    from byte.lint import LintService

    # Create a file and commit it
    test_file = application.root_path("test_file.py")
    test_file.write_text("print('hello')")

    git_service = application.make(GitService)
    repo = await git_service.get_repo()
    repo.index.add([str(test_file.relative_to(application.root_path()))])
    repo.index.commit("Add test file")

    # Delete the file
    test_file.unlink()

    service = application.make(LintService)
    results = await service.lint_changed_files()

    # Should not include the deleted file
    assert not any(r.file == test_file for r in results)


@pytest.mark.asyncio
async def test_lint_files_creates_lint_file_for_each_command(application: Application):
    """Test that lint_files creates LintFile for each command/file combination."""
    from byte.lint import LintService
    from byte.lint.config import LintCommand

    # Add multiple commands
    application["config"].lint.commands = [
        LintCommand(command=["echo", "lint1"], languages=["python"]),
        LintCommand(command=["echo", "lint2"], languages=["python"]),
    ]

    # Create a test file
    test_file = application.root_path("test.py")
    test_file.write_text("print('test')")

    service = application.make(LintService)
    results = await service.lint_files([test_file])

    # Should have 2 results (one per command)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_lint_files_filters_by_language(application: Application):
    """Test that lint_files filters files by language."""
    from byte.lint import LintService
    from byte.lint.config import LintCommand

    # Add command that only handles python
    application["config"].lint.commands = [
        LintCommand(command=["echo", "lint"], languages=["python"]),
    ]

    # Create python and javascript files
    py_file = application.root_path("test.py")
    py_file.write_text("print('test')")

    js_file = application.root_path("test.js")
    js_file.write_text("console.log('test')")

    service = application.make(LintService)
    results = await service.lint_files([py_file, js_file])

    # Should only lint python file
    assert len(results) == 1
    assert results[0].file == py_file


@pytest.mark.asyncio
async def test_lint_files_processes_all_files_when_no_languages(application: Application):
    """Test that lint_files processes all files when no languages specified."""
    from byte.lint import LintService
    from byte.lint.config import LintCommand

    # Add command with no language filter
    application["config"].lint.commands = [
        LintCommand(command=["echo", "lint"], languages=[]),
    ]

    # Create files of different types
    py_file = application.root_path("test.py")
    py_file.write_text("print('test')")

    js_file = application.root_path("test.js")
    js_file.write_text("console.log('test')")

    service = application.make(LintService)
    results = await service.lint_files([py_file, js_file])

    # Should lint both files
    assert len(results) == 2


@pytest.mark.asyncio
async def test_lint_files_processes_all_files_with_wildcard(application: Application):
    """Test that lint_files processes all files when languages contains '*'."""
    from byte.lint import LintService
    from byte.lint.config import LintCommand

    # Add command with wildcard
    application["config"].lint.commands = [
        LintCommand(command=["echo", "lint"], languages=["*"]),
    ]

    # Create files of different types
    py_file = application.root_path("test.py")
    py_file.write_text("print('test')")

    js_file = application.root_path("test.js")
    js_file.write_text("console.log('test')")

    service = application.make(LintService)
    results = await service.lint_files([py_file, js_file])

    # Should lint both files
    assert len(results) == 2


@pytest.mark.asyncio
async def test_lint_files_executes_commands(application: Application):
    """Test that lint_files executes lint commands."""
    from byte.lint import LintService

    # Create a test file
    test_file = application.root_path("test.py")
    test_file.write_text("print('test')")

    service = application.make(LintService)
    results = await service.lint_files([test_file])

    # Should have executed command
    assert len(results) > 0
    assert results[0].exit_code is not None


@pytest.mark.asyncio
async def test_lint_files_captures_stdout(application: Application):
    """Test that lint_files captures stdout from commands."""
    from byte.lint import LintService
    from byte.lint.config import LintCommand

    # Add command that outputs to stdout
    application["config"].lint.commands = [
        LintCommand(command=["echo", "test output"], languages=["python"]),
    ]

    test_file = application.root_path("test.py")
    test_file.write_text("print('test')")

    service = application.make(LintService)
    results = await service.lint_files([test_file])

    assert len(results) > 0
    assert "test output" in results[0].stdout


@pytest.mark.asyncio
async def test_lint_files_captures_stderr(application: Application):
    """Test that lint_files captures stderr from commands."""
    from byte.lint import LintService
    from byte.lint.config import LintCommand

    # Add command that outputs to stderr using {file} placeholder
    application["config"].lint.commands = [
        LintCommand(command=["sh", "-c", "echo error message for {file} >&2"], languages=["python"]),
    ]

    test_file = application.root_path("test.py")
    test_file.write_text("print('test')")

    service = application.make(LintService)
    results = await service.lint_files([test_file])

    assert len(results) > 0
    assert "error message" in results[0].stderr


@pytest.mark.asyncio
async def test_lint_files_records_exit_code(application: Application):
    """Test that lint_files records exit code from commands."""
    from byte.lint import LintService
    from byte.lint.config import LintCommand

    # Add command that exits with non-zero
    application["config"].lint.commands = [
        LintCommand(command=["sh", "-c", "exit 1"], languages=["python"]),
    ]

    test_file = application.root_path("test.py")
    test_file.write_text("print('test')")

    service = application.make(LintService)
    results = await service.lint_files([test_file])

    assert len(results) > 0
    assert results[0].exit_code == 1


@pytest.mark.asyncio
async def test_display_results_summary_returns_false_when_no_issues(application: Application):
    """Test that display_results_summary returns (False, []) when no issues found."""
    from byte.lint import LintFile, LintService

    service = application.make(LintService)

    # Create successful lint result
    test_file = application.root_path("test.py")
    lint_result = LintFile(
        command=["echo", "test"],
        file=test_file,
        exit_code=0,
    )

    do_fix, failed = await service.display_results_summary([lint_result])

    assert do_fix is False
    assert failed == []


@pytest.mark.asyncio
async def test_display_results_summary_returns_failed_commands(application: Application, mocker):
    """Test that display_results_summary returns failed commands."""

    from byte.lint import LintFile, LintService

    service = application.make(LintService)

    # Create failed lint result
    test_file = application.root_path("test.py")
    lint_result = LintFile(
        command=["echo", "test"],
        file=test_file,
        exit_code=1,
        stderr="error message",
    )

    mocker.patch.object(application["console"], "confirm", return_value=False)

    _, failed = await service.display_results_summary([lint_result])

    assert len(failed) == 1
    assert failed[0] == lint_result


@pytest.mark.asyncio
async def test_format_lint_errors_wraps_errors_in_boundaries(application: Application):
    """Test that format_lint_errors wraps errors in boundary tags."""
    from byte.lint import LintFile, LintService

    service = application.make(LintService)

    test_file = application.root_path("test.py")
    lint_result = LintFile(
        command=["echo", "test"],
        file=test_file,
        exit_code=1,
        stderr="lint error",
    )

    formatted = service.format_lint_errors([lint_result])

    assert "<error" in formatted
    assert "</error>" in formatted
    assert "lint error" in formatted


@pytest.mark.asyncio
async def test_format_lint_errors_includes_file_source(application: Application):
    """Test that format_lint_errors includes file source in metadata."""
    from byte.lint import LintFile, LintService

    service = application.make(LintService)

    test_file = application.root_path("test.py")
    lint_result = LintFile(
        command=["echo", "test"],
        file=test_file,
        exit_code=1,
        stderr="lint error",
    )

    formatted = service.format_lint_errors([lint_result])

    assert str(test_file) in formatted
    assert "source=" in formatted


@pytest.mark.asyncio
async def test_format_lint_errors_uses_stdout_when_no_stderr(application: Application):
    """Test that format_lint_errors uses stdout when stderr is empty."""
    from byte.lint import LintFile, LintService

    service = application.make(LintService)

    test_file = application.root_path("test.py")
    lint_result = LintFile(
        command=["echo", "test"],
        file=test_file,
        exit_code=1,
        stdout="stdout message",
        stderr="",
    )

    formatted = service.format_lint_errors([lint_result])

    assert "stdout message" in formatted


@pytest.mark.asyncio
async def test_format_lint_errors_includes_header(application: Application):
    """Test that format_lint_errors includes header message."""
    from byte.lint import LintFile, LintService

    service = application.make(LintService)

    test_file = application.root_path("test.py")
    lint_result = LintFile(
        command=["echo", "test"],
        file=test_file,
        exit_code=1,
        stderr="error",
    )

    formatted = service.format_lint_errors([lint_result])

    assert "Fix The Following Lint Errors" in formatted
