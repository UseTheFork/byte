---
name: V. Strict Python Standards
---

All Python code MUST comply with the project's ruff configuration (target `py314`, line-length 120, space indentation), ssort import ordering, and 4-space indentation as defined in `.editorconfig`. Pre-commit hooks MUST pass before any code is committed. Type hints MUST be used for all public function signatures. Files MUST use LF line endings and UTF-8 encoding. Rationale: Automated enforcement eliminates style debates and maintains codebase consistency.
