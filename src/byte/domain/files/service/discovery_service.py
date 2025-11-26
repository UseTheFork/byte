import os
from pathlib import Path
from typing import List, Optional, Set

from byte.core.logging import log
from byte.core.service.base_service import Service
from byte.domain.files.service.ignore_service import FileIgnoreService


class FileDiscoveryService(Service):
    """Service for discovering and filtering project files with gitignore support.

    Scans the project directory on boot to build a cached index of all files,
    respecting .gitignore patterns for efficient file operations and completions.
    Usage: `files = discovery.get_files()` -> all non-ignored project files
    """

    async def boot(self) -> None:
        """Initialize file discovery by scanning project with ignore patterns."""
        self._all_files: Set[Path] = set()
        await self._scan_project_files()

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
                    log.debug(f"Discovered file: {file_path}")
                    self._all_files.add(file_path)

    async def _is_ignored(self, path: Path) -> bool:
        """Check if a path should be ignored using FileIgnoreService.

        Delegates to the centralized ignore service for consistent
        filtering across all file operations.
        """
        ignore_service = await self.make(FileIgnoreService)
        is_ignored = await ignore_service.is_ignored(path)
        return is_ignored

    async def get_files(self, extension: Optional[str] = None) -> List[Path]:
        """Get all discovered files, optionally filtered by extension.

        Returns cached file list for fast access, with optional filtering
        by file extension for language-specific operations.
        Usage: `py_files = discovery.get_files('.py')` -> Python files only
        """
        files = list(self._all_files)

        if extension:
            files = [f for f in files if f.suffix == extension]

        return sorted(files, key=lambda p: str(p.relative_to(self._config.project_root)))

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

        return sorted(all_matches, key=lambda p: str(p.relative_to(self._config.project_root)))

    async def add_file(self, path: Path) -> bool:
        """Add a newly discovered file to the cache.

        Usage: `discovery.add_file(Path("new_file.py"))` -> adds to cache
        """
        if await self._is_ignored(path):
            return False

        if path.is_file() and path not in self._all_files:
            self._all_files.add(path)
            return True
        return False

    async def remove_file(self, path: Path) -> bool:
        """Remove a file from the cache when it's deleted.

        Usage: `discovery.remove_file(Path("deleted.py"))` -> removes from cache
        """
        if path in self._all_files:
            self._all_files.discard(path)
            return True
        return False

    async def refresh(self) -> None:
        """Refresh the file cache by rescanning the project directory.

        Useful when files are added/removed outside of the application
        or when gitignore patterns change during development.
        Usage: `discovery.refresh()` -> updates cached file list
        """
        self._all_files.clear()

        # Refresh ignore patterns from FileIgnoreService
        ignore_service = await self.make(FileIgnoreService)
        await ignore_service.refresh()

        await self._scan_project_files()
