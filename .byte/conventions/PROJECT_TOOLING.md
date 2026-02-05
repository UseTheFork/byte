---
name: tooling-convention
description: Build systems (uv), package managers, bundlers, task runners, linting/formatting tools (ruff, ssort, prettier), pre-commit hooks, and tooling configuration standards. Use when configuring project tooling, adding dependencies, or setting up development workflows.
---

# Tooling Convention

## Package Manager & Build System

**uv** - Modern Python package installer and resolver:

```bash
# Install dependencies
uv sync

# Run commands in project environment
uv run byte
uv run pytest

# Add dependencies
uv add package-name
uv add --dev package-name  # Development only
```

**Build backend** - `uv_build` in `pyproject.toml`:

```toml
[build-system]
requires = ["uv_build>=0.8.10,<0.10.0"]
build-backend = "uv_build"
```

**Dependency groups** - Separate dev and docs dependencies:

```toml
[dependency-groups]
dev = ["pytest>=8.4.2", "ruff>=0.12.12", "ssort>=0.16.0"]
mkdocs = ["mkdocs>=1.6.1", "mkdocs-material>=9.6.21"]
```

## Linting & Formatting

**ruff** - Primary linter and formatter (replaces black, isort, flake8):

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "FURB", "G", "I", "ICN", "ISC", "LOG", "PIE", "PT", "Q", "RSE", "RUF", "T10", "UP"]
ignore = ["E501", "ISC001", "RUF012", "UP006", "UP007"]  # Line length, implicit string concat, etc.

[tool.ruff.format]
indent-style = "space"
line-ending = "lf"

[tool.ruff.lint.isort]
combine-as-imports = true
```

**ssort** - Statement sorting for Python files:

```bash
uv run ssort src/
```

**prettier** - Markdown formatting:

```bash
prettier --write docs/**/*.md
```

## Pre-commit Hooks

**Configuration** - `.pre-commit-config.yaml` with local hooks:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff-format
        entry: uv run ruff format --force-exclude
        language: system
        types_or: [python, pyi]
        require_serial: true
      - id: ruff
        name: ruff
        entry: uv run ruff check --fix --force-exclude
        language: system
        types_or: [python, pyi]
        require_serial: true
```

**Key patterns**:

- Use `local` repo for project-specific tools
- Prefix commands with `uv run` for environment isolation
- Use `--force-exclude` to respect `.gitignore`
- Set `require_serial: true` for formatters to avoid race conditions

## Task Runner

**just** - Command runner for common tasks:

```justfile
[doc('Run Pytest With Coverage Report')]
test:
    uv run pytest --cov-report=xml --cov-report=term-missing --cov=src/byte src/tests/

[doc('Display the list of recipes')]
default:
  @just --list
```

**Patterns**:

- Use `[doc('...')]` attribute for help text
- Prefix with `uv run` for Python commands
- Keep recipes focused and composable

## Testing Configuration

**pytest** - Test framework with async support:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["src/tests"]
markers = ["vcr: record/replay HTTP via VCR"]
norecursedirs = "tmp.* build benchmark _site OLD"
addopts = "--record-mode=once"
```

**Coverage** - Via pytest-cov:

```bash
uv run pytest --cov-report=xml --cov-report=term-missing --cov=src/byte src/tests/
```

## Documentation Tooling

**MkDocs** - Static site generator with Material theme:

```yaml
theme:
  name: material
  features:
    - navigation.instant
    - navigation.sections
    - content.code.copy
    - content.tabs.link
  palette:
    scheme: slate
    primary: black

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.tabbed:
      alternate_style: true

plugins:
  - search
  - mkdocstrings
```

**Build and serve**:

```bash
uv run mkdocs serve  # Local preview
uv run mkdocs build  # Production build
```

## Editor Configuration

**.editorconfig** - Cross-editor consistency:

```ini
root = true

[*]
indent_style = space
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.yml]
indent_size = 2

[*.py]
indent_size = 4
```

## Release Automation

**python-semantic-release** - Automated versioning and changelog:

```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
build_command = """
  uv lock --upgrade-package byte-ai-cli
  uv build
"""
commit_subject = "chore: release v{version}"
commit_parser = "conventional"
tag_format = "v{version}"

[tool.semantic_release.commit_parser_options]
minor_tags = ["feat"]
patch_tags = ["fix", "perf"]
allowed_tags = ["feat", "fix", "perf", "build", "ops", "chore", "ci", "docs", "style", "refactor", "test"]
```

**Conventional commits** - Required for automated releases:

- `feat:` → minor version bump
- `fix:`, `perf:` → patch version bump
- `BREAKING CHANGE:` → major version bump

## Tooling Standards

**Always use uv run** - Never install globally:

```bash
# ✓ Correct
uv run pytest
uv run ruff check

# ✗ Wrong
pytest  # May use wrong environment
```

**Lock file updates** - Explicit upgrade commands:

```bash
uv lock --upgrade-package byte-ai-cli  # Upgrade specific package
uv lock --upgrade  # Upgrade all
```

**Python version** - Enforce minimum in pyproject.toml:

```toml
[project]
requires-python = ">=3.12"

[tool.ruff]
target-version = "py312"
```

**Entry points** - Define CLI commands:

```toml
[project.scripts]
byte = "byte.main:cli"
```
