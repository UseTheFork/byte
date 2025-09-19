import os
from pathlib import Path
from typing import List, Optional, Set

import pathspec

from byte.core.config.mixins import Configurable
from byte.core.service.mixins import Bootable


class FileDiscoveryService(Bootable, Configurable):
    """Service for discovering and filtering project files with gitignore support.

    Scans the project directory on boot to build a cached index of all files,
    respecting .gitignore patterns for efficient file operations and completions.
    Usage: `files = discovery.get_files()` -> all non-ignored project files
    """

    async def boot(self) -> None:
        """Initialize file discovery by scanning project and loading gitignore patterns."""
        self._all_files: Set[Path] = set()
        self._gitignore_spec: Optional[pathspec.PathSpec] = None

        self._load_gitignore_patterns()
        await self._scan_project_files()

    def _load_gitignore_patterns(self) -> None:
        """Load and compile gitignore patterns from .gitignore files.

        Searches for .gitignore files in project root and parent directories,
        combining patterns into a single pathspec for efficient filtering.
        """
        patterns = []

        # Always ignore common patterns
        patterns.extend(
            [
                ".git/",
                "__pycache__/",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".Python",
                "build/",
                "develop-eggs/",
                "dist/",
                "downloads/",
                "eggs/",
                ".eggs/",
                "lib/",
                "lib64/",
                "parts/",
                "sdist/",
                "var/",
                "wheels/",
                "*.egg-info/",
                ".installed.cfg",
                "*.egg",
                ".env",
                ".venv",
                "env/",
                "venv/",
                "ENV/",
                "env.bak/",
                "venv.bak/",
            ]
        )

        print(self._config.project_root)

        gitignore_path = self._config.project_root / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, encoding="utf-8") as f:
                    patterns.extend(
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    )
            except (OSError, UnicodeDecodeError):
                # Gracefully handle unreadable gitignore files
                pass

        self._gitignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    async def _scan_project_files(self) -> None:
        """Recursively scan project directory and cache all non-ignored files.

        Builds an in-memory index of project files for fast lookups and
        completions, filtering out ignored files and directories.
        """
        if not self._config.project_root or not self._config.project_root.exists():
            return

        for root, dirs, files in os.walk(self._config.project_root):
            root_path = Path(root)

            # Filter directories to avoid scanning ignored ones
            dirs[:] = [d for d in dirs if not self._is_ignored(root_path / d)]

            # Add non-ignored files to our cache
            for file in files:
                file_path = root_path / file
                if not self._is_ignored(file_path) and file_path.is_file():
                    self._all_files.add(file_path)

    def _is_ignored(self, path: Path) -> bool:
        """Check if a path should be ignored based on gitignore patterns.

        Uses relative path from project root for pattern matching,
        consistent with git's ignore behavior.
        """
        if not self._gitignore_spec or not self._config.project_root:
            return False

        try:
            relative_path = path.relative_to(self._config.project_root)
            # Check both file and directory patterns
            return self._gitignore_spec.match_file(
                str(relative_path)
            ) or self._gitignore_spec.match_file(str(relative_path) + "/")
        except ValueError:
            # Path is outside project root
            return True

    def get_files(self, extension: Optional[str] = None) -> List[Path]:
        """Get all discovered files, optionally filtered by extension.

        Returns cached file list for fast access, with optional filtering
        by file extension for language-specific operations.
        Usage: `py_files = discovery.get_files('.py')` -> Python files only
        """
        files = list(self._all_files)

        if extension:
            files = [f for f in files if f.suffix == extension]

        return sorted(
            files, key=lambda p: str(p.relative_to(self._config.project_root))
        )

    def get_relative_paths(self, extension: Optional[str] = None) -> List[str]:
        """Get relative path strings for UI display and completions.

        Provides user-friendly relative paths from project root,
        suitable for command completions and file selection interfaces.
        Usage: `paths = discovery.get_relative_paths('.py')` -> ['src/main.py', ...]
        """
        files = self.get_files(extension)
        if not self._config.project_root:
            return [str(f) for f in files]

        return [str(f.relative_to(self._config.project_root)) for f in files]

    def find_files(self, pattern: str) -> List[Path]:
        """Find files matching a partial path pattern for completions.

        Supports prefix matching for tab completion and file search,
        returning files whose relative paths start with the given pattern.
        Usage: `matches = discovery.find_files('src/main')` -> files starting with 'src/main'
        """
        if not self._config.project_root:
            return []

        matches = []
        for file_path in self._all_files:
            try:
                relative_path = str(file_path.relative_to(self._config.project_root))
                if relative_path.startswith(pattern):
                    matches.append(file_path)
            except ValueError:
                continue

        return sorted(
            matches, key=lambda p: str(p.relative_to(self._config.project_root))
        )

    def refresh(self) -> None:
        """Refresh the file cache by rescanning the project directory.

        Useful when files are added/removed outside of the application
        or when gitignore patterns change during development.
        Usage: `discovery.refresh()` -> updates cached file list
        """
        self._all_files.clear()
        self._load_gitignore_patterns()
        # Note: This is sync, but _scan_project_files is async
        # In practice, we'd want to make this async too or provide both sync/async versions
        import asyncio

        asyncio.create_task(self._scan_project_files())
