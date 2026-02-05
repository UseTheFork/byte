---
name: comment-standards
description: Docstring format, inline comment style, when to comment vs self-documenting code, and documentation best practices for the Byte codebase. Use when writing or reviewing comments and docstrings.
---

# Comment Standards

## Docstring Format

**Required for all public classes, methods, and functions** - Brief summary, blank line, then usage examples:

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

**Multi-paragraph format** - Additional context after blank line, usage examples last:

```python
async def generate_context_prompt(self) -> tuple[list[str], list[str]]:
    """Generate structured file lists for read-only and editable files.

    Returns two separate lists of formatted file strings, enabling
    flexible assembly in the prompt context. The AI can understand
    its permissions and make appropriate suggestions for each file type.

    Returns:
        Tuple of (read_only_files, editable_files) as lists of strings

    Usage: `read_only, editable = await service.generate_context_prompt()`
    """
```

**Type hints in signature, not docstring** - Args section only for complex parameters:

```python
def _configure_model_schema(self, model_id: str, model_type: str) -> ModelSchema:
    """Configure a ModelSchema from models_data.yaml.

    Args:
        model_id: The model identifier (e.g., "claude-sonnet-4-5")
        model_type: Either "main" or "weak"

    Returns:
        Configured ModelSchema instance

    Raises:
        ByteConfigException: If model not found in models_data
    """
```

**Usage examples with arrows** - Show input → output pattern:

```python
async def get_project_files(self, extension: Optional[str] = None) -> List[str]:
    """Get all project files as relative path strings.

    Uses the discovery service to provide fast access to all project files,
    optionally filtered by extension for language-specific operations.
    Usage: `py_files = service.get_project_files('.py')` -> Python files
    """
```

**Minimal docstrings for simple methods** - One-line summary only:

```python
def get_active_agent(self) -> Type[Agent]:
    """Get the currently active agent type.

    Usage: `current_agent = agent_service.get_active_agent()`
    """
```

**Class docstrings** - Purpose, integration points, usage example:

```python
class FileService(Service):
    """Simplified domain service for file context management with project discovery.

    Manages the active set of files available to the AI assistant, with
    integrated project file discovery for better completions and file operations.
    Loads all project files on boot for fast reference and completion.
    Usage: `await file_service.add_file("main.py", FileMode.EDITABLE)`
    """
```

## Inline Comments

**Explain "why" not "what"** - Code should be self-documenting:

```python
# ✓ Good - explains business logic
# Only add files that are in the discovery service
if not path_obj.is_file() or str(path_obj) not in discovered_file_paths:
    return False

# ✗ Bad - describes obvious code
# Check if path is a file
if not path_obj.is_file():
    return False
```

**Separate line above code** - Not trailing:

```python
# ✓ Good
# Use placeholder if set, then clear it
default = self.placeholder or ""
self.placeholder = None

# ✗ Bad
default = self.placeholder or ""  # Use placeholder if set
self.placeholder = None  # Clear it
```

**Section markers** - For logical groupings:

```python
# Get modified and staged files
for item in self._repo.index.diff(None):
    changed_files.append(Path(str(item.a_path)))

# Get untracked files if requested
if include_untracked:
    for untracked_file in self._repo.untracked_files:
        changed_files.append(Path(untracked_file))
```

**Match statements** - Explain each case:

```python
match diff_item.change_type:
    case "A":
        msg = f"new: {diff_item.a_path}"
    case "D":
        msg = f"deleted: {diff_item.a_path}"
    case "M":
        msg = f"modified: {diff_item.a_path}"
```

## When to Comment vs Self-Document

**Comment for:**

- Non-obvious business logic or requirements
- Design decisions and rationale
- Integration points with other domains
- Workarounds or temporary solutions (with TODO/FIXME)
- Complex algorithms or data transformations

**Self-document with:**

- Descriptive variable names: `discovered_file_paths` not `paths`
- Small, focused functions with clear names
- Type hints for all parameters and returns
- Structured code flow (early returns, guard clauses)

**Examples:**

```python
# ✓ Comment needed - explains non-obvious requirement
# Only add if file is in the discovery service
if key in self._context_files:
    return False

# ✓ Self-documenting - clear intent from code
if not user_input.strip():
    return

# ✓ Comment needed - explains integration point
# Emit event for UI updates and other interested components
await self.emit(payload)
```

## Special Tags

**TODO** - Planned features or improvements:

```python
# TODO: Doc String
async def _emit_file_context_event(self, file: str, type, content: str) -> str:
    """ """
```

**FIXME** - Known bugs requiring attention:

```python
# FIXME: Handle binary files properly
```

**NOTE** - Important implementation details:

```python
# NOTE: This must run before provider registration
```

## Documentation Best Practices

**Empty docstrings for incomplete implementations** - Mark with TODO:

```python
# TODO: Doc String
async def _emit_file_context_event(self, file: str, type, content: str) -> str:
    """ """
```

**Internal methods** - Brief purpose, no usage examples needed:

```python
def _create_runnable(self, context: AssistantContextSchema) -> Runnable:
    """Create the runnable chain from context configuration.

    Assembles the prompt and model based on the mode (main or weak AI).
    If tools are provided, binds them to the model with parallel execution disabled.
    """
```

**Utility functions** - Show input/output pattern:

```python
def extract_json_from_message(message) -> str | None:
    """Extract partial JSON content from a message object.

    Usage: `json_str = extract_json_from_message(message)`
    """
```

**Avoid redundant comments** - Don't restate the obvious:

```python
# ✗ Bad
# Initialize file service
def boot(self, **kwargs) -> None:
    self._context_files: Dict[str, FileContext] = {}

# ✓ Good - no comment needed, code is clear
def boot(self, **kwargs) -> None:
    self._context_files: Dict[str, FileContext] = {}
```
