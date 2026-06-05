---
id: minimal-lean-docstrings
name: Minimal / Lean Docstrings
order: 70
---
All public methods and classes MUST have a one-line docstring describing *what* they do, written in imperative mood (e.g., "Resolve a service", "Register a binding"). `Args:` and `Returns:` sections SHOULD only be included when the parameter names and type hints alone do not tell the full story. `Returns: None` MUST NOT appear in any docstring. `Usage:` sections MUST NOT be used; use `Example:` sparingly if a usage illustration is genuinely needed. Private methods MAY omit a docstring entirely when the implementation is trivial.
