# Comment Style Guide

## Formatting

- Start with capital letter, end with period for complete sentences
- Place on separate line above code, not trailing; use inline sparingly
- Space after comment character: `# `, `// `

## Docstrings (Python)

- Required for all public classes, methods, and functions
- Format: Brief summary, blank line, usage examples
- Include type hints in signature, not docstring

Example:

```python
async def add_file(self, path: Union[str, PathLike], mode: FileMode) -> bool:
    """Add a file to the active context for AI awareness.

    Usage: `await service.add_file("config.py", FileMode.READ_ONLY)`
    Usage: `await service.add_file("src/*.py", FileMode.EDITABLE)` -> adds all Python files
    """
```

## Function Comments (Other Languages)

- Brief purpose, usage example with input/output, optional type signature

Example (Nix):

```nix
# fetch user's public keys from github .keys url
# `fetchKeys "username"` -> "ssh-rsa AAAA...== username@hostname"
fetchKeys = username: (builtins.fetchurl "https://github.com/${username}.keys");
```

## Special Tags

- `TODO:` planned features; `FIXME:` known bugs; `NOTE:` non-obvious implementation

## Philosophy

- Explain "why" not "what" - code should be self-documenting
- Focus on business logic, design decisions, and non-obvious requirements
