from os import PathLike
from typing import Dict, List, Optional, Union

from byte.core.config.configurable import Configurable
from byte.core.mixins.bootable import Bootable
from byte.domain.lint.config import LintConfig


class LintService(Bootable, Configurable):
    """Domain service for code linting and formatting operations.

    Orchestrates multiple linting commands configured in config.yaml to analyze
    and optionally fix code quality issues. Integrates with git service to
    target only changed files for efficient linting workflows.
    Usage: `await lint_service.lint_changed_files()` -> runs configured linters on git changes
    """

    _config: LintConfig

    async def lint_changed_files(
        self, file_extensions: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """Run configured linters on git changed files.

        Args:
            file_extensions: Filter files by extensions (e.g., ['.py', '.js'])

        Returns:
            Dict mapping command names to lists of issues found

        Usage: `results = await lint_service.lint_changed_files(['.py'])` -> lint changed Python files
        """
        print(self._config)
        # TODO: Implement linting of changed files
        return {}

    async def lint_files(
        self, file_paths: List[Union[str, PathLike]]
    ) -> Dict[str, List[str]]:
        """Run configured linters on specified files.

        Args:
            file_paths: Specific files to lint

        Returns:
            Dict mapping command names to lists of issues found

        Usage: `results = await lint_service.lint_files(["main.py", "utils.py"])`
        """
        # TODO: Implement linting of specific files
        return {}
