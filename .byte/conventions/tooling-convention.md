---
name: tooling-convention
description: Standards for build systems, package managers, dev tools, linting, formatting, and tooling configuration. Use when setting up project tooling, configuring CI/CD, or managing dependencies.
---

# Tooling Standards

## Package Management

**Primary**: `uv` (Python package manager and build backend)

```toml
# pyproject.toml
[build-system]
requires = ["uv_build>=0.8.10,<0.10.0"]
build-backend = "uv_build"
```

**Commands**:

- `uv sync` - Install dependencies (use `--all-groups` for dev deps)
- `uv run <command>` - Execute commands in virtual environment
- `uv build` - Build distribution artifacts

**Lock file**: `uv.lock` must be committed and updated during releases

**Dependency groups**:

```toml
[dependency-groups]
dev = ["pytest>=8.4.2", "ruff>=0.12.12", ...]
mkdocs = ["mkdocs>=1.6.1", ...]
```

## Python Version Management

- **Version**: Python 3.12 (specified in `.python-version`)
- **Minimum**: `>=3.12` in `pyproject.toml`
- **Nix integration**: `flake.nix` provides reproducible dev environment via direnv

## Linting & Formatting

**Ruff** (linter + formatter):

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "FURB", "G", "I", "ICN", "ISC", "LOG", "PIE", "PT", "Q", "RSE", "RUF", "T10", "UP"]
ignore = ["E501", "ISC001", "RUF012", ...]  # Specific exclusions

[tool.ruff.format]
indent-style = "space"
line-ending = "lf"

[tool.ruff.lint.isort]
combine-as-imports = true
```

**Commands**:

- `uv run ruff format --force-exclude` - Format code
- `uv run ruff check --fix --force-exclude` - Lint and auto-fix

**ssort** (import sorting):

- `uv run ssort` - Sort imports within files

**keep-sorted** (list/block sorting):

- Wrap sorted blocks with `# keep-sorted start` / `# keep-sorted end`
- Used for: import lists, config fields, select/ignore lists
- Example:

```python
# keep-sorted start
from byte.analytics import AnalyticsServiceProvider
from byte.cli import CLIServiceProvider
from byte.config import ByteConfig
# keep-sorted end
```

**Prettier** (Markdown):

- `prettier --write` for `.md` files

## Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
  - repo: local
    hooks:
      - id: ruff-format
        entry: uv run ruff format --force-exclude
        language: system
        types_or: [python, pyi]
      - id: ruff
        entry: uv run ruff check --fix --force-exclude
        language: system
        types_or: [python, pyi]
```

**Note**: ssort, ruff, prettier, keep-sorted run automatically via pre-commit. Don't suggest running them manually.

## Testing

**pytest** with async support:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["src/tests"]
markers = ["vcr: record/replay HTTP via VCR"]
addopts = "--record-mode=once"
```

**Run tests**:

```bash
just test  # Runs: uv run pytest --cov-report=xml --cov-report=term-missing --cov=src/byte src/tests/
```

**Test organization**:

- Tests in `src/tests/` mirroring `src/byte/` structure
- VCR cassettes in `cassettes/` subdirectories for HTTP recording
- Use `pytest-recording`, `pytest-asyncio`, `pytest-mock`, `pytest-cov`

## Task Runner

**just** (command runner):

```justfile
[doc('Run Pytest With Coverage Report')]
test:
    uv run pytest --cov-report=xml --cov-report=term-missing --cov=src/byte src/tests/
```

## Documentation

**MkDocs** with Material theme:

```yaml
# mkdocs.yml
theme:
  name: material
  features:
    - navigation.instant
    - content.code.copy
    - content.tabs.link
```

**Build/deploy**:

- `uv run --all-groups mkdocs gh-deploy --force` (CI only)
- Auto-generated docs via scripts:
  - `uv run python src/scripts/commands_to_md.py` → `docs/reference/commands.md`
  - `uv run python src/scripts/settings_to_md.py` → `docs/reference/settings.md`
  - `uv run python src/scripts/update_models.py` → `src/byte/llm/resources/models_data.yaml`

## Release Management

**python-semantic-release**:

```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:project.version"]
build_command = """
  uv lock --upgrade-package byte-ai-cli
  uv build
"""
commit_parser = "conventional"
tag_format = "v{version}"
```

**Conventional commits**:

- `feat:` → minor version bump
- `fix:`, `perf:` → patch version bump
- Other: `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `ops`, `test`

**Release workflow**:

1. Staging branch → prepare docs/models
2. Main branch → semantic-release creates tag/release
3. Deploy to PyPI
4. Sync branches: main → staging → development

## CI/CD

**GitHub Actions**:

- `uv sync --all-groups` for dependency installation
- `astral-sh/setup-uv@v7` action with caching
- Artifacts: distribution files (`dist/**`) and `uv.lock`

**Dependabot**:

```yaml
updates:
  - package-ecosystem: "uv"
    schedule: { interval: "weekly" }
    target-branch: "development"
```

## Editor Configuration

**EditorConfig**:

```ini
[*]
indent_style = space
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.py]
indent_size = 4

[*.yml]
indent_size = 2
```

**VSCode**:

```json
{
  "editor.insertSpaces": true,
  "ty.path": [".venv/bin/ty"]
}
```

## Nix Development Environment

**flake.nix** provides:

- Python 3.12 via `uv2nix` workspace
- Dev tools: `just`, `pre-commit`, `uv`, `nodejs`, `prettier`, `alejandra`, `yamlfmt`, `keep-sorted`
- Reproducible via direnv (`.envrc`)

**Usage**: `direnv allow` to auto-load environment

## Key Principles

1. **uv-first**: All Python operations via `uv run` or `uv sync`
2. **Auto-formatting**: Pre-commit handles all formatting; don't suggest manual runs
3. **Sorted blocks**: Use `keep-sorted` comments for maintainability
4. **Conventional commits**: Required for semantic versioning
5. **Lock file discipline**: Commit `uv.lock`, update during releases
6. **Script-generated docs**: Never manually edit `commands.md`, `settings.md`, or `models_data.yaml`
