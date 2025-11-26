from pathlib import Path
from typing import Optional

import pathspec

from byte.core.logging import log
from byte.core.service.base_service import Service


class FileIgnoreService(Service):
    """Service for managing file ignore patterns from gitignore and configuration.

    Consolidates ignore pattern loading and matching logic to avoid duplication
    across file discovery and watching services. Combines .gitignore rules with
    custom configuration patterns for comprehensive file filtering.
    Usage: `is_ignored = await ignore_service.is_ignored(file_path)`
    """

    async def boot(self) -> None:
        """Initialize service by loading and compiling ignore patterns."""
        self._gitignore_spec: Optional[pathspec.PathSpec] = None
        await self._load_ignore_patterns()

    async def _load_ignore_patterns(self) -> None:
        """Load and compile ignore patterns from .gitignore files and config.

        Searches for .gitignore in project root and combines with custom
        configuration patterns into a single pathspec for efficient filtering.
        """
        patterns = []

        # Load project-specific .gitignore only if we have a valid project root
        if self._config.project_root is not None:
            gitignore_path = self._config.project_root / ".gitignore"
            if gitignore_path.exists():
                try:
                    with open(gitignore_path, encoding="utf-8") as f:
                        patterns.extend(line.strip() for line in f if line.strip() and not line.startswith("#"))
                except (OSError, UnicodeDecodeError):
                    # Gracefully handle unreadable gitignore files
                    pass

            # Load ignore patterns from configuration
            patterns.extend(self._config.files.ignore)

        # Log all patterns being used for debugging
        if patterns:
            log.debug(f"Loaded {len(patterns)} ignore patterns:")
            for pattern in patterns:
                log.debug(f"  - {pattern}")
        else:
            log.debug("No ignore patterns loaded")

        self._gitignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    async def is_ignored(self, path: Path) -> bool:
        """Check if a path should be ignored based on loaded patterns.

        Uses relative path from project root for pattern matching,
        consistent with git's ignore behavior. Checks both file and
        directory patterns to handle all gitignore pattern types.
        Usage: `if await ignore_service.is_ignored(file_path): continue`
        """
        if not self._gitignore_spec or not self._config.project_root:
            return False

        try:
            relative_path = path.relative_to(self._config.project_root)
            relative_str = str(relative_path)

            # Check if the path itself matches
            if self._gitignore_spec.match_file(relative_str) or self._gitignore_spec.match_file(relative_str + "/"):
                return True

            # Check if any parent directory matches an ignore pattern
            # This handles files inside ignored directories like __pycache__/file.pyc
            for parent in relative_path.parents:
                if parent == Path("."):
                    break
                parent_str = str(parent)
                if self._gitignore_spec.match_file(parent_str) or self._gitignore_spec.match_file(parent_str + "/"):
                    return True

            return False
        except ValueError:
            # Path is outside project root, consider it ignored
            return True

    async def refresh(self) -> None:
        """Reload ignore patterns from filesystem and configuration.

        Useful when .gitignore or configuration changes during development,
        ensuring file filtering stays up-to-date with project rules.
        Usage: `await ignore_service.refresh()` -> reloads patterns
        """
        await self._load_ignore_patterns()

    def get_pathspec(self) -> Optional[pathspec.PathSpec]:
        """Get the compiled pathspec for advanced filtering use cases.

        Provides direct access to the pathspec for services that need
        more control over pattern matching behavior.
        Usage: `spec = ignore_service.get_pathspec()`
        """
        return self._gitignore_spec
