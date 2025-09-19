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

        await self._load_gitignore_patterns()
        await self._scan_project_files()

    async def _load_gitignore_patterns(self) -> None:
        """Load and compile gitignore patterns from .gitignore files.

        Searches for .gitignore files in project root and parent directories,
        combining patterns into a single pathspec for efficient filtering.
        """
        patterns = []

        # Load project-specific .gitignore only if we have a valid project root
        if self._config.project_root is not None:
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

            # Also load .byte/.ignore file for project-specific ignore patterns
            byte_ignore_path = self._config.byte_dir / ".ignore"
            if byte_ignore_path.exists():
                try:
                    with open(byte_ignore_path, encoding="utf-8") as f:
                        patterns.extend(
                            line.strip()
                            for line in f
                            if line.strip() and not line.startswith("#")
                        )
                except (OSError, UnicodeDecodeError):
                    # Gracefully handle unreadable .ignore files
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
            dirs[:] = [d for d in dirs if not await self._is_ignored(root_path / d)]

            # Add non-ignored files to our cache
            for file in files:
                file_path = root_path / file
                if not await self._is_ignored(file_path) and file_path.is_file():
                    self._all_files.add(file_path)

    async def _is_ignored(self, path: Path) -> bool:
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

    async def get_files(self, extension: Optional[str] = None) -> List[Path]:
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

    async def get_relative_paths(self, extension: Optional[str] = None) -> List[str]:
        """Get relative path strings for UI display and completions.

        Provides user-friendly relative paths from project root,
        suitable for command completions and file selection interfaces.
        Usage: `paths = discovery.get_relative_paths('.py')` -> ['src/main.py', ...]
        """
        files = await self.get_files(extension)
        if not self._config.project_root:
            return [str(f) for f in files]

        return [str(f.relative_to(self._config.project_root)) for f in files]

    async def find_files(self, pattern: str) -> List[Path]:
        """Find files matching a partial path pattern for completions.

        Supports fuzzy matching for tab completion and file search. Matches files
        where the pattern appears anywhere in the relative path, prioritizing
        exact prefix matches, then fuzzy matches by relevance score.
        Usage: `matches = discovery.find_files('boot')` -> includes 'byte/bootstrap.py'
        """
        if not self._config.project_root:
            return []

        pattern_lower = pattern.lower()
        exact_matches = []
        fuzzy_matches = []

        for file_path in self._all_files:
            try:
                relative_path = str(file_path.relative_to(self._config.project_root))
                relative_path_lower = relative_path.lower()

                # Exact prefix match gets highest priority
                if relative_path_lower.startswith(pattern_lower):
                    exact_matches.append(file_path)
                # Fuzzy match: pattern appears anywhere in the path
                elif pattern_lower in relative_path_lower:
                    # Calculate relevance score based on pattern position and file name
                    file_name = file_path.name.lower()
                    if pattern_lower in file_name:
                        # Pattern in filename gets higher score
                        score = len(pattern) / len(file_name)
                    else:
                        # Pattern in directory path gets lower score
                        score = len(pattern) / len(relative_path)
                    fuzzy_matches.append((file_path, score))
            except ValueError:
                continue

        # Sort fuzzy matches by relevance score (higher is better)
        fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
        fuzzy_files = [match[0] for match in fuzzy_matches]

        # Combine exact matches first, then fuzzy matches
        all_matches = exact_matches + fuzzy_files

        return sorted(
            all_matches, key=lambda p: str(p.relative_to(self._config.project_root))
        )

    async def refresh(self) -> None:
        """Refresh the file cache by rescanning the project directory.

        Useful when files are added/removed outside of the application
        or when gitignore patterns change during development.
        Usage: `discovery.refresh()` -> updates cached file list
        """
        self._all_files.clear()
        await self._load_gitignore_patterns()
        await self._scan_project_files()
