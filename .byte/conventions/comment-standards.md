---
name: comment-standards
description: Standards for docstrings, inline comments, and documentation in Python code. Use when writing or reviewing code comments and docstrings.
---

# Comment Standards

## Docstring Format

### Class Docstrings

- **One-line summary** describing the class purpose
- **Optional extended description** explaining domain context, integration points, or architectural role
- **Usage examples** showing instantiation or common patterns
- Use present tense ("Manages", "Provides", "Handles")

```python
class FileService(Service):
    """Simplified domain service for file context management with project discovery.

    Manages the active set of files available to the AI assistant, with
    integrated project file discovery for better completions and file operations.
    Loads all project files on boot for fast reference and completion.
    Usage: `await file_service.add_file("main.py", FileMode.EDITABLE)`
    """
```

### Method Docstrings

- **One-line summary** in imperative mood ("Get", "Create", "Validate")
- **Args section** only when parameters need clarification beyond type hints
- **Returns section** only for complex return types or when behavior isn't obvious
- **Raises section** only for exceptions that callers should handle
- **Usage examples** showing concrete invocation patterns with expected results

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

### Function Docstrings

- **One-line summary** sufficient for simple utility functions
- **Args/Returns** only when not obvious from signature
- **Usage example** showing typical invocation

```python
def extract_json_from_message(message) -> str | None:
    """Extract partial JSON content from a message object.

    Usage: `json_str = extract_json_from_message(message)`
    """
```

### Module Docstrings

- **One-line summary** at top of file for modules with abstract base classes or complex parsing logic
- Omit for straightforward implementation files

```python
"""Base service for parsing and validating files with YAML frontmatter."""
```

## Usage Examples Pattern

**Format**: `` `code` -> expected result`` or `` `code` `` alone

```python
# Single usage
Usage: `lang = get_language_from_filename('script.py')` -> 'Python'

# Multiple usages showing different scenarios
Usage: `await service.add_file("config.py", FileMode.READ_ONLY)`
Usage: `await service.add_file("src/*.py", FileMode.EDITABLE)` -> adds all Python files

# Showing context
Usage: `graph = builder.build()` -> returns configured state graph
```

## Inline Comments

### When to Use Inline Comments

**DO comment**:

- Non-obvious business logic or domain rules
- Workarounds or temporary solutions
- Complex algorithms or data transformations
- State transitions or lifecycle events
- Regex patterns or complex string operations

```python
# Check if path contains wildcard patterns
if "*" in path_str or "?" in path_str or "[" in path_str:
    # Handle glob patterns - resolve relative to base path
```

**DON'T comment**:

- Self-explanatory code with clear variable/method names
- Type conversions or simple assignments
- Standard patterns (loops, conditionals with obvious intent)

### Inline Comment Style

- Use `#` with single space after
- Place above the code block, not at end of line (except for brief clarifications)
- Use sentence fragments without periods for brevity
- Group related operations under a single comment

```python
# Separate files by mode for clear AI understanding
read_only = [f for f in self._context_files.values() if f.mode == FileMode.READ_ONLY]
editable = [f for f in self._context_files.values() if f.mode == FileMode.EDITABLE]
```

## Self-Documenting Code vs Comments

### Prefer Self-Documenting Code

**Good** - Clear naming eliminates need for comments:

```python
def _format_agent_name(self, agent_name: str) -> str:
    """Convert agent class name to readable headline case.

    Usage: "CoderAgent" -> "Coder Agent"
    """
    spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", agent_name)
    return spaced
```

**Avoid** - Comment explaining what code should express:

```python
# This function formats the agent name
def format_name(self, name: str) -> str:
    # Add spaces before capitals
    result = re.sub(r"(?<!^)(?=[A-Z])", " ", name)
    return result
```

### When Comments Add Value

- **Domain context**: "Only add files that are in the discovery service to ensure they are valid project files"
- **Why not what**: "Re-prompt for actual response" (explains intent, not mechanics)
- **Constraints**: "Only replace first occurrence" (clarifies deliberate limitation)
- **Integration points**: "Emit event for UI updates and other interested components"

## Documentation Best Practices

### Conciseness

- One-line docstrings for simple functions/methods
- Extended descriptions only when architectural context matters
- Omit Args/Returns when type hints and names are sufficient

### Consistency

- All public classes have docstrings
- All public methods have at least one-line docstrings
- Private methods (`_method`) have docstrings only when logic is complex
- Abstract methods always document expected behavior

### Maintenance

- Update docstrings when behavior changes
- Remove outdated comments immediately
- Keep usage examples accurate and tested

### Type Hints Over Comments

```python
# Good - types in signature
def parse_attributes(self, attr_string: str) -> dict[str, str]:

# Avoid - types in docstring
def parse_attributes(self, attr_string):
    """Parse attributes.

    Args:
        attr_string (str): String containing attributes

    Returns:
        dict[str, str]: Parsed attributes
    """
```

### Abstract Method Documentation

- Document the contract, not implementation
- Specify what subclasses must provide
- Include validation expectations

```python
@abstractmethod
def validate_metadata_fields(self, metadata: dict) -> list[str]:
    """Validate that only allowed fields are present.

    Args:
        metadata: Parsed YAML frontmatter dictionary

    Returns:
        List of validation error messages. Empty list means valid.

    Usage: `errors = service.validate_metadata_fields(metadata)`
    """
    pass
```
