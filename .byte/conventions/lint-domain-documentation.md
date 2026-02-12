---
name: lint-domain-documentation
description: Domain documentation for src/byte/lint - code linting and formatting operations. Use when working with lint configuration, implementing lint commands, or integrating linting into agent workflows.
---

# Lint Domain Documentation

## Domain Purpose

The lint domain orchestrates code quality checks by executing configured linting tools on changed files. It integrates with git to target only modified files and provides AI-friendly error formatting for automated fixes via the coder agent.

**Core Responsibilities:**

- Execute multiple linting commands per file based on language
- Display interactive results with fix prompts
- Format lint errors for AI consumption with boundary tags
- Validate lint configuration before execution

## Key Components

### LintService (`service/lint_service.py`)

Main orchestrator for linting operations.

**Key Methods:**

```python
await lint_service.validate()  # Check config before execution
await lint_service.lint_changed_files()  # Lint git changes
await lint_service.lint_files(file_paths)  # Lint specific files
lint_service.format_lint_errors(failed_commands)  # Format for AI
```

**Execution Model:**

- Groups commands by file, runs sequentially per file
- Executes files in parallel with progress tracking
- Filters out removed files (only lints existing files)

### LintCommand (`command/lint_command.py`)

CLI command that stages changes, runs linters, and optionally invokes CoderAgent to fix errors.

**Flow:**

1. Stage git changes
2. Execute lint service
3. Display results summary
4. If user confirms, pass errors to CoderAgent for automated fixes

### Configuration (`config.py`)

```python
class LintCommand(BaseModel):
    command: List[str]  # e.g., ['ruff', 'check', '--fix']
    languages: List[str]  # e.g., ['python', 'php'], empty = all files

class LintConfig(BaseModel):
    enable: bool = False
    commands: List[LintCommand] = []
```

**Placeholder Support:**

- Use `{file}` in command parts: `['mypy', '{file}']`
- Without placeholder, file path appended: `['ruff', 'check']` → `['ruff', 'check', 'path/to/file.py']`

**Language Filtering:**

- Empty `languages` list = process all files
- `["*"]` in languages = process all files
- Specific languages = case-insensitive match using Pygments lexer detection

## Data Models

### LintFile (`types.py`)

Result of executing one lint command on one file.

```python
@dataclass
class LintFile:
    command: List[str]
    file: Path
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
```

### LintCommandType (`types.py`)

Groups results by command (used for display).

```python
@dataclass
class LintCommandType:
    command: List[str]
    results: List[LintFile]
```

## Business Logic Patterns

### Sequential Per-File Execution

Commands run sequentially for each file to avoid conflicts (e.g., formatters modifying files):

```python
async def _lint_file_sequential(self, file_path: Path, lint_files: List[LintFile], git_root: str):
    file_task_id = self._progress.add_task(f"{file_path.name}", total=len(lint_files))
    results = []
    for lint_file in lint_files:
        result = await self._execute_lint_command(lint_file, file_task_id, git_root)
        results.append(result)
    return results
```

### Error Formatting for AI

Wraps errors in boundary tags for structured parsing:

```python
Boundary.open(BoundaryType.ERROR, meta={"type": "lint", "source": str(lint_file.file)})
f"{error_msg}"
Boundary.close(BoundaryType.ERROR)
```

### Result Display Strategy

Shows first 3 failed files per command with truncated errors, counts remaining failures.

## API Contracts

### LintService.validate()

**Returns:** `bool` (always True if no exception)  
**Raises:** `LintConfigException` if `enable=False` or no commands configured  
**Usage:** Call before executing lint operations

### LintService.lint_changed_files()

**Returns:** `List[LintFile]` with execution results  
**Side Effects:** Displays live progress UI, filters removed files  
**Integration:** Calls `GitService.get_changed_files()`

### LintService.display_results_summary()

**Returns:** `tuple[bool, List[LintFile]]` - (user_wants_fix, failed_commands)  
**Side Effects:** Prints panel, prompts user for confirmation  
**Display Logic:** Groups by command, shows 3 files max per command

### LintService.format_lint_errors()

**Args:** `List[LintFile]` (failed commands only)  
**Returns:** `str` with boundary-wrapped errors  
**Format:** `**Fix The Following Lint Errors**\n\n<ERROR>...</ERROR>`

## Integration Points

### Git Domain

- `GitService.get_changed_files()` - source of files to lint
- `GitService.stage_changes()` - called before linting in command
- `GitService.get_repo()` - provides working directory for subprocess execution

### Agent Domain

- `AgentService.execute_agent({"errors": formatted_errors}, CoderAgent)` - automated fix workflow
- Errors formatted with `Boundary` tags for structured parsing

### CLI Domain

- `console.print_panel()` - results display
- `console.confirm()` - user interaction for fix prompt
- `Progress` and `Live` - real-time linting progress

### Support Domain

- `get_language_from_filename()` - Pygments-based language detection for filtering
- `Boundary` - structured error wrapping for AI consumption

## Domain-Specific Conventions

### Exception Handling

- Raise `LintConfigException` for configuration issues (not runtime errors)
- Command execution errors set `exit_code=-1` and populate `stderr`

### Subprocess Execution

- Always run in `git_root` directory for consistent paths
- Capture both stdout and stderr
- Log command, exit code, and output at debug level

### Progress Tracking

- One task per file (not per command)
- Advance on command completion
- Transient display (clears after completion)

### Language Detection

- Use `get_language_from_filename()` from support utils
- Case-insensitive language matching
- Fallback: process all files if no language detected

### Configuration Validation

- Check `enable` flag first
- Require at least one command configured
- Provide actionable error messages with config path references
