"""Perform a local release: version bump, build, and publish to PyPI.

Usage: uv run python src/scripts/release.py

Steps:
  Step: Update documentation and models
  Step: Stage and commit generated files
  Step: Build next version artifacts
  Step: Check if a new release was detected; exit early if not
  Step: Stage uv.lock via git
  Step: Create release commit and tag
  Step: Create GitHub release
  Step: Publish to PyPI using uv publish
"""

import json
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

console = Console()


def run_command(command: list[str], description: str) -> subprocess.CompletedProcess:
    """Run a shell command and exit with error if it fails.

    Args:
        command: Command to run as a list of strings
        description: Human-readable description of what the command does

    Returns:
        Completed process result if successful

    Raises:
        SystemExit: If command fails (non-zero return code)
    """
    console.print(f"[bold cyan]→[/] {description}")
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        console.print(f"[bold red]✗[/] {description} failed with exit code {result.returncode}")
        if result.stdout:
            console.print("STDOUT:", result.stdout)
        if result.stderr:
            console.print("STDERR:", result.stderr)
        sys.exit(result.returncode)

    console.print(f"[bold green]✓[/] {description}")
    return result


def check_new_release(version_output: str) -> bool:
    """Check if a new release was detected from semantic-release output.

    Parses the JSON output from semantic-release to determine if a release occurred.

    Returns:
        True if released == 'true', False otherwise
    """
    try:
        lines = version_output.strip().split("\n")
        for line in lines:
            if line.startswith("{"):
                data = json.loads(line)
                return data.get("released") == "true"
    except json.JSONDecodeError, ValueError:
        pass
    return False


def main() -> None:
    """Execute local release workflow."""
    env_loaded = load_dotenv(Path(__file__).resolve().parents[2] / ".env")

    if env_loaded:
        console.print("[bold green]✓[/] Loaded .env")
    else:
        console.print("[bold red]✗[/] Failed to load .env")
        return

    console.print("Starting release process...\n")

    # Step: Update documentation and models
    console.print("=== Step: Update documentation and models ===")
    run_command(
        ["uv", "run", "python", "src/scripts/commands_to_md.py"],
        "Generating commands documentation",
    )
    run_command(
        ["uv", "run", "python", "src/scripts/requests_to_md.py"],
        "Generating gateway requests documentation",
    )
    run_command(
        ["uv", "run", "python", "src/scripts/settings_to_md.py"],
        "Generating settings documentation",
    )
    run_command(
        ["uv", "run", "python", "src/scripts/update_models.py"],
        "Updating models data",
    )

    # Step: Stage and commit generated files
    console.print("\n=== Step: Stage and commit generated files ===")
    run_command(["git", "add", "docs/references"], "Staging docs/references")
    run_command(
        ["git", "add", "src/byte/llm/resources/models_data.yaml"],
        "Staging models_data.yaml",
    )
    diff_result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if diff_result.returncode == 0:
        console.print("[dim]i[/] No generated file changes to commit, skipping")
    else:
        run_command(
            ["git", "commit", "-m", "docs: update generated documentation and models"],
            "Committing generated files",
        )

    # Step: Build next version artifacts
    console.print("\n=== Step: Build next version artifacts ===")
    result = run_command(
        ["uv", "run", "semantic-release", "-v", "version"],
        "Building version and artifacts",
    )

    # Step: Check if a new release was detected
    console.print("\n=== Step: Check for new release ===")
    if not check_new_release(result.stdout + result.stderr):
        console.print("[dim]i[/] No new release detected. Exiting.")
        sys.exit(0)
    console.print("[bold green]✓[/] New release detected")

    # Step: Stage uv.lock for version commit
    console.print("\n=== Step: Stage lock file ===")
    run_command(["git", "add", "uv.lock"], "Staging uv.lock")

    # Step: Create release commit and tag
    console.print("\n=== Step: Create release commit and tag ===")
    run_command(
        ["uv", "run", "semantic-release", "-vv", "--strict", "version", "--skip-build"],
        "Creating release commit and tag",
    )

    # Step: Create GitHub release
    console.print("\n=== Step: Create GitHub release ===")
    run_command(["uv", "run", "semantic-release", "publish"], "Publishing GitHub release")

    # Step: Publish to PyPI
    console.print("\n=== Step: Publish to PyPI ===")
    run_command(["uv", "publish"], "Publishing to PyPI")

    console.print("\n[bold green]✓[/] Release complete!")


if __name__ == "__main__":
    main()


# semantic-release -v version --skip-build --no-commit --no-tag --no-changelog
# uv lock --upgrade-package byte-ai-cli
# git add uv.lock
# gh release create v2.1.0 --title "v2.1.0" --notes "so many changes it crashes the api"
# uv build
# gh release upload v2.1.0 dist/*
# uv run --all-groups mkdocs gh-deploy --force
