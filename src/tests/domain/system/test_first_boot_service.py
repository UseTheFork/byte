from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from byte.core.config.config import ByteConfig
from byte.domain.system.service.first_boot_service import FirstBootService


@pytest.fixture
def first_boot_service():
    """Provide a FirstBootService instance for testing.

    Usage: `def test_something(first_boot_service): ...`
    """
    return FirstBootService()


@pytest.fixture
def mock_console():
    """Provide a mock Console for testing print methods.

    Usage: `def test_something(mock_console): ...`
    """
    console = MagicMock()
    return console


def test_is_first_boot_when_config_missing(tmp_project_root: Path, monkeypatch):
    """Test that is_first_boot returns True when config file doesn't exist."""
    # Patch BYTE_CONFIG_FILE to point to temp directory
    config_file = tmp_project_root / ".byte" / "config.yaml"
    monkeypatch.setattr("byte.domain.system.service.first_boot_service.BYTE_CONFIG_FILE", config_file)

    service = FirstBootService()
    assert service.is_first_boot() is True


def test_is_first_boot_when_config_exists(tmp_project_root: Path, monkeypatch):
    """Test that is_first_boot returns False when config file exists."""
    # Create config file
    byte_dir = tmp_project_root / ".byte"
    byte_dir.mkdir(exist_ok=True)
    config_file = byte_dir / "config.yaml"
    config_file.write_text("model: sonnet\n")

    # Patch BYTE_CONFIG_FILE
    monkeypatch.setattr("byte.domain.system.service.first_boot_service.BYTE_CONFIG_FILE", config_file)

    service = FirstBootService()
    assert service.is_first_boot() is False


def test_run_if_needed_skips_when_not_first_boot(tmp_project_root: Path, monkeypatch):
    """Test that run_if_needed returns False and skips initialization when config exists."""
    # Create config file
    byte_dir = tmp_project_root / ".byte"
    byte_dir.mkdir(exist_ok=True)
    config_file = byte_dir / "config.yaml"
    config_file.write_text("model: sonnet\n")

    # Patch BYTE_CONFIG_FILE
    monkeypatch.setattr("byte.domain.system.service.first_boot_service.BYTE_CONFIG_FILE", config_file)

    service = FirstBootService()
    result = service.run_if_needed()

    assert result is False


def test_find_binary_returns_path_when_found(first_boot_service: FirstBootService):
    """Test that find_binary returns Path when binary exists."""
    # Test with a binary that should exist on most systems
    result = first_boot_service.find_binary("python3")

    assert result is not None
    assert isinstance(result, Path)
    assert result.exists()


def test_find_binary_returns_none_when_not_found(first_boot_service: FirstBootService):
    """Test that find_binary returns None when binary doesn't exist."""
    result = first_boot_service.find_binary("nonexistent-binary-xyz123")

    assert result is None


def test_print_info(first_boot_service: FirstBootService, mock_console):
    """Test that print_info formats message correctly."""
    first_boot_service._console = mock_console

    first_boot_service.print_info("Test message")

    mock_console.print.assert_called_once_with("  Test message")


def test_print_success(first_boot_service: FirstBootService, mock_console):
    """Test that print_success formats message with checkmark."""
    first_boot_service._console = mock_console

    first_boot_service.print_success("Success message")

    mock_console.print.assert_called_once_with("[green]✓[/green] Success message")


def test_print_error(first_boot_service: FirstBootService, mock_console):
    """Test that print_error formats message with X."""
    first_boot_service._console = mock_console

    first_boot_service.print_error("Error message")

    mock_console.print.assert_called_once_with("[red]✗[/red] Error message")


def test_print_warning(first_boot_service: FirstBootService, mock_console):
    """Test that print_warning formats message with warning symbol."""
    first_boot_service._console = mock_console

    first_boot_service.print_warning("Warning message")

    mock_console.print.assert_called_once_with("[yellow]⚠[/yellow] Warning message")


def test_setup_byte_directories(tmp_project_root: Path, monkeypatch, mock_console):
    """Test that _setup_byte_directories creates all necessary directories."""
    byte_dir = tmp_project_root / ".byte"
    config_file = byte_dir / "config.yaml"

    # Patch paths
    monkeypatch.setattr("byte.domain.system.service.first_boot_service.BYTE_CONFIG_FILE", config_file)
    monkeypatch.setattr("byte.domain.system.service.first_boot_service.BYTE_CACHE_DIR", byte_dir / "cache")

    service = FirstBootService()
    service._console = mock_console

    service._setup_byte_directories()

    # Verify directories were created
    assert byte_dir.exists()
    assert (byte_dir / "conventions").exists()
    assert (byte_dir / "context").exists()
    assert (byte_dir / "cache").exists()


def test_setup_gitignore_creates_new_file(tmp_project_root: Path, monkeypatch, mock_console):
    """Test that _setup_gitignore creates .gitignore with byte patterns when it doesn't exist."""
    # Patch PROJECT_ROOT
    monkeypatch.setattr("byte.domain.system.service.first_boot_service.PROJECT_ROOT", tmp_project_root)

    service = FirstBootService()
    service._console = mock_console

    # Mock Menu to auto-confirm
    with patch("byte.domain.system.service.first_boot_service.Menu") as mock_menu:
        mock_menu.return_value.confirm.return_value = True

        service._setup_gitignore()

    # Verify .gitignore was created with correct patterns
    gitignore_path = tmp_project_root / ".gitignore"
    assert gitignore_path.exists()

    content = gitignore_path.read_text()
    assert ".byte/cache/*" in content
    assert ".byte/session_context/*" in content


def test_setup_gitignore_appends_missing_patterns(tmp_project_root: Path, monkeypatch, mock_console):
    """Test that _setup_gitignore appends missing patterns to existing .gitignore."""
    # Create existing .gitignore with one pattern
    gitignore_path = tmp_project_root / ".gitignore"
    gitignore_path.write_text("*.pyc\n.byte/cache/*\n")

    # Patch PROJECT_ROOT
    monkeypatch.setattr("byte.domain.system.service.first_boot_service.PROJECT_ROOT", tmp_project_root)

    service = FirstBootService()
    service._console = mock_console

    # Mock Menu to auto-confirm
    with patch("byte.domain.system.service.first_boot_service.Menu") as mock_menu:
        mock_menu.return_value.confirm.return_value = True

        service._setup_gitignore()

    # Verify missing pattern was added
    content = gitignore_path.read_text()
    assert ".byte/cache/*" in content
    assert ".byte/session_context/*" in content
    assert "*.pyc" in content  # Original content preserved


def test_setup_gitignore_skips_when_all_patterns_exist(tmp_project_root: Path, monkeypatch, mock_console):
    """Test that _setup_gitignore does nothing when all patterns already exist."""
    # Create .gitignore with all patterns
    gitignore_path = tmp_project_root / ".gitignore"
    original_content = "*.pyc\n.byte/cache/*\n.byte/session_context/*\n"
    gitignore_path.write_text(original_content)

    # Patch PROJECT_ROOT
    monkeypatch.setattr("byte.domain.system.service.first_boot_service.PROJECT_ROOT", tmp_project_root)

    service = FirstBootService()
    service._console = mock_console

    service._setup_gitignore()

    # Verify content unchanged
    assert gitignore_path.read_text() == original_content


def test_init_llm_returns_selected_provider(mock_console):
    """Test that _init_llm returns the selected provider."""
    service = FirstBootService()
    service._console = mock_console

    # Mock Menu to return "anthropic"
    with patch("byte.domain.system.service.first_boot_service.Menu") as mock_menu:
        mock_menu.return_value.select.return_value = "anthropic"

        result = service._init_llm()

    assert result == "anthropic"


def test_init_llm_defaults_to_first_provider_on_cancel(mock_console):
    """Test that _init_llm defaults to first provider when user cancels."""
    service = FirstBootService()
    service._console = mock_console

    # Mock Menu to return None (cancelled)
    with patch("byte.domain.system.service.first_boot_service.Menu") as mock_menu:
        mock_menu.return_value.select.return_value = None

        result = service._init_llm()

    assert result == "anthropic"  # First in the list


def test_init_web_finds_chrome(mock_console):
    """Test that _init_web configures Chrome when found."""
    service = FirstBootService()
    service._console = mock_console

    config = ByteConfig()

    # Mock find_binary to return a Chrome path
    with patch.object(service, "find_binary") as mock_find:
        mock_find.return_value = Path("/usr/bin/google-chrome-stable")

        result = service._init_web(config)

    assert result.web.chrome_binary_location == Path("/usr/bin/google-chrome-stable")
    assert result.web.enable is True


def test_init_web_falls_back_to_chromium(mock_console):
    """Test that _init_web falls back to Chromium when Chrome not found."""
    service = FirstBootService()
    service._console = mock_console

    config = ByteConfig()

    # Mock find_binary to return None for Chrome, Path for Chromium
    with patch.object(service, "find_binary") as mock_find:
        mock_find.side_effect = [None, Path("/usr/bin/chromium")]

        result = service._init_web(config)

    assert result.web.chrome_binary_location == Path("/usr/bin/chromium")
    assert result.web.enable is True


def test_init_web_disables_when_no_browser_found(mock_console):
    """Test that _init_web disables web commands when no browser found."""
    service = FirstBootService()
    service._console = mock_console

    config = ByteConfig()

    # Mock find_binary to return None for both
    with patch.object(service, "find_binary") as mock_find:
        mock_find.return_value = None

        result = service._init_web(config)

    assert result.web.enable is False


def test_init_files_enables_watch_when_confirmed(mock_console):
    """Test that _init_files enables file watching when user confirms."""
    service = FirstBootService()
    service._console = mock_console

    config = ByteConfig()

    # Mock Menu to confirm
    with patch("byte.domain.system.service.first_boot_service.Menu") as mock_menu:
        mock_menu.return_value.confirm.return_value = True

        result = service._init_files(config)

    assert result.files.watch.enable is True


def test_init_files_disables_watch_when_declined(mock_console):
    """Test that _init_files disables file watching when user declines."""
    service = FirstBootService()
    service._console = mock_console

    config = ByteConfig()

    # Mock Menu to decline
    with patch("byte.domain.system.service.first_boot_service.Menu") as mock_menu:
        mock_menu.return_value.confirm.return_value = False

        result = service._init_files(config)

    assert result.files.watch.enable is False
