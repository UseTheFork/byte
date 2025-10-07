# Comment Styling Guide

This guide outlines the best practices for writing comments in this repository. The goal is to maintain clarity and consistency across all code, regardless of the programming language.

## General Principles

1. **Explain the "Why", Not the "What"**: Code should be self-documenting. Use comments to explain complex logic, design decisions, or the intent behind a piece of code that might not be immediately obvious.

1. **Keep it Concise**: Write short, clear sentences. Avoid long narratives.

1. **Placement**:

   - Place comments on the line immediately preceding the code block they describe.
   - Inline comments can be used to clarify individual lines, arguments, or variable declarations.

## Formatting

- Start comments with the comment character followed by a single space (e.g., `# `, `// `).
- Use complete sentences with proper capitalization and punctuation.
- For multi-line comments, each line should begin with the comment character.

## Function Documentation

For functions, methods, or reusable components, provide a summary that includes:

1. A brief description of its purpose.
1. An example of usage, including input and expected output.
1. (Optional) Type signatures if the language is dynamically typed.

### Example (Nix)

```nix
# a basic function to fetch a specified user's public keys from github .keys url
# `fetchKeys "username` -> "ssh-rsa AAAA...== username@hostname"
#@ String -> String
fetchKeys = username: (builtins.fetchurl "https://github.com/${username}.keys");
```

## Special Tags

Use standard tags to highlight specific information:

- `TODO:` for planned features or improvements.
- `FIXME:` for known issues that need to be addressed.
# Comment Style Guide

## General Formatting
- Use inline comments sparingly; prefer clear code over explanatory comments
- Start comments with capital letter, end with period for complete sentences
- Place comments on separate line above code, not trailing
- Use double-quote docstrings for all modules, classes, and functions

## Docstring Patterns
- Required for all public classes, methods, and functions
- Format: Brief summary, blank line, detailed explanation, blank line, usage examples
- Include type information via type hints, not in docstrings
- Usage examples should show real-world invocation patterns

Example:
```python
async def add_file(self, path: Union[str, PathLike], mode: FileMode) -> bool:
    """Add a file to the active context for AI awareness.

    Supports wildcard patterns like 'byte/*' to add multiple files at once.
    Only adds files that are available in the FileDiscoveryService to ensure
    they are valid project files that respect gitignore patterns.
    Usage: `await service.add_file("config.py", FileMode.READ_ONLY)`
    Usage: `await service.add_file("src/*.py", FileMode.EDITABLE)` -> adds all Python files
    """
```

## Special Tags
- `TODO:` - Planned feature or enhancement, include description
- `FIXME:` - Known bug or issue that needs attention
- `NOTE:` - Important explanation about non-obvious implementation
- Avoid `HACK:` and `XXX:` - refactor code instead

## Explain "Why" Not "What"
- ❌ `# Set the container` (obvious from code)
- ✅ `# Store reference for complex initialization where container is needed beyond register/boot`
- Focus on business logic, architectural decisions, and non-obvious requirements
