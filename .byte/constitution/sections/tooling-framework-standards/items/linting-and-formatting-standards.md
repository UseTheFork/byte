---
id: linting-and-formatting-standards
name: Linting and Formatting Standards
order: 20
section_id: tooling-framework-standards
---
All Python code MUST pass Ruff linting and formatting checks as configured in `pyproject.toml` under `[tool.ruff]`. The lint pipeline runs in order: `ssort` (statement sorting) → `ruff format` (formatting) → `ruff check --fix` (lint with auto-fix). Key configuration: target Python 3.14, line length 120, space indentation, LF line endings, and `combine-as-imports` enabled for isort. All code MUST be free of Ruff errors before merge.
