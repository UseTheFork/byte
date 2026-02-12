---
name: git-domain-documentation
description: Domain documentation for src/byte/git - git repository operations, conventional commits, and version control integration. Use when working with git functionality, commit workflows, or understanding git domain architecture.
---

# Git Domain Documentation

## Domain Purpose

The git domain handles repository operations, conventional commit generation, and version control integration. It provides AI-powered commit message generation following the Conventional Commits specification, automated staging, and commit workflow orchestration.

**Core Responsibilities:**

- Git repository operations (staging, committing, diffing)
- Conventional commit message generation and formatting
- Commit workflow automation with linting integration
- User interaction for commit approval and breaking changes
- Multi-commit planning and execution

## Key Components

### Services

**GitService** (`service/git_service.py`)

- Low-level git operations via GitPython
- File change detection and diff generation
- Staging/unstaging operations
- Repository state management

```python
# Usage patterns
changed_files = await git_service.get_changed_files(include_untracked=True)
await git_service.stage_changes()
diff_data = await git_service.get_diff()  # Returns structured diff with metadata
await git_service.commit("feat: add feature")
```

**CommitService** (`service/commit_service.py`)

- Conventional commit formatting and validation
- Commit prompt building from diffs
- Commit plan processing (multi-commit workflows)
- Breaking change confirmation flow

```python
# Build AI prompt from staged changes
prompt = await commit_service.build_commit_prompt()

# Format with config-aware field inclusion
formatted = await commit_service.format_conventional_commit(commit_message)

# Process multi-commit plan
await commit_service.process_commit_plan(commit_plan)
```

### Data Models

**CommitMessage** (`schemas.py`)

- Structured conventional commit representation
- Fields: `type`, `scope`, `commit_message`, `breaking_change`, `breaking_change_message`, `body`
- `format()` method produces conventional commit string

**CommitGroup** (extends CommitMessage)

- Adds `files: list[str]` for multi-commit planning
- `format_with_files()` includes file list in output

**CommitPlan** (`schemas.py`)

- Container for multiple CommitGroup objects
- Used by CommitPlanAgent for atomic commit separation

### Commands

**CommitCommand** (`command/commit_command.py`)

- Entry point: `/commit`
- Orchestrates full commit workflow:
  1. Stage all changes
  2. Validate changes exist
  3. Run linters (if configured)
  4. Fix lint errors via CoderAgent (optional)
  5. Re-stage after fixes
  6. Prompt for commit type (Single/Plan)
  7. Generate commit message via AI
  8. Execute commit(s)

### Validators

**CommitValidator** (`validators/commit_validator.py`)

- User confirmation for generated commits
- Handles both single commits and commit plans
- Collects change requests for AI revision
- Returns `ValidationError` objects with context for regeneration

## Business Logic

### Conventional Commit Formatting

Follows [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

**Type Definitions** (from `commit_service.py`):

- `feat`: New features
- `fix`: Bug fixes
- `refactor`: Code restructuring without behavior change
- `perf`: Performance improvements
- `style`: Formatting changes
- `test`: Test additions/corrections
- `build`: Build system changes
- `ops`: Operational/infrastructure changes
- `docs`: Documentation only
- `chore`: Maintenance tasks

**Formatting Rules:**

- Description: lowercase first char, no trailing period, imperative mood
- Max description length: configurable (default 72 chars)
- Breaking changes: `!` suffix + optional `BREAKING CHANGE:` footer
- Scope/body/breaking changes: config-controlled inclusion

### Diff Generation

`GitService.get_diff()` returns structured diff data:

```python
[
    {
        "file": "path/to/file.py",
        "change_type": "M",  # A=added, M=modified, D=deleted, R=renamed
        "diff": "unified diff content or None for binary/deleted",
        "msg": "modified: path/to/file.py",
        "is_renamed": False,
        "is_modified": True,
        "is_new": False,
        "is_deleted": False,
    }
]
```

**Binary file handling:** Detects `\0` bytes, excludes diff content
**Deleted files:** No diff content included

### Commit Prompt Building

`CommitService.build_commit_prompt()` creates AI-ready prompts:

1. Extract staged diff via `get_diff()`
2. Wrap each file's diff in `<context type="Diff" change_type="M" file="path">` boundaries
3. Create summary section with `<context type="Files">` containing change messages
4. Return concatenated prompt string

### Commit Plan Processing

Multi-commit workflow (`process_commit_plan`):

1. Unstage all files via `git_service.reset()`
2. For each CommitGroup:
   - Stage only files in group
   - Handle deletions via `remove()` instead of `add()`
   - Format and commit with group's message
3. Creates atomic, logically separated commits

## Configuration

**GitConfig** (`config.py`) - accessed via `app["config"].git`:

```python
enable_scopes: bool = False  # Include scope in commits
enable_breaking_changes: bool = True  # Breaking change detection
enable_body: bool = True  # Include body in commits
scopes: List[str] = ["api", "auth", "cli", ...]  # Available scopes
description_guidelines: List[str] = []  # Custom guidelines
max_description_length: int = 72  # Description char limit
```

**Config-aware formatting:** `format_conventional_commit()` respects config flags, omitting disabled fields from output.

## Integration Points

### Agent Domain

- **CommitAgent:** Generates single conventional commit from diff
- **CommitPlanAgent:** Generates multi-commit plan with file grouping
- **CoderAgent:** Fixes lint errors before committing
- Uses `CommitValidator` for user approval loop

### Lint Domain

- `CommitCommand` invokes `LintService` after staging
- Displays lint results, prompts for fixes
- Re-stages after CoderAgent fixes

### CLI Domain

- Uses `UserInteractive` mixin for prompts
- `console.print_*_panel()` for formatted output
- `prompt_for_confirmation()`, `prompt_for_select()` for user input

### Files Domain

- Integrates with file watching/discovery (indirect)
- Commit workflow operates on staged files

## Domain Patterns

### Service Initialization

```python
def boot(self, *args, **kwargs) -> None:
    self.git_service = self.app.make(GitService)
```

Services use `boot()` for dependency injection, not `__init__`.

### Error Handling with Retry

`GitService.commit()` implements retry loop:

- Catches commit exceptions
- Displays error panel
- Prompts to re-stage and retry
- Preserves originally staged files for retry

### Boundary-based Prompts

Uses `Boundary` objects for structured AI context:

```python
Boundary.open(BoundaryType.CONTEXT, meta={"type": "Diff", "file": "path"})
# content
Boundary.close(BoundaryType.CONTEXT)
```

### Config-driven Behavior

All formatting respects `GitConfig` flags - services check config before including optional fields.

### Validation with Context

`CommitValidator` returns `ValidationError` with:

- `context`: Formatted commit message
- `message`: User's requested changes
  Enables AI to revise with full context.

## API Contracts

### GitService Interface

```python
async def get_changed_files(include_untracked: bool = True) -> List[Path]
async def get_diff() -> List[dict]  # Structured diff data
async def stage_changes(force: bool = False) -> None
async def commit(commit_message: str) -> None
async def reset(file_path: str | None = None) -> None
async def add(file_path: str) -> None
async def remove(file_path: str) -> None
```

### CommitService Interface

```python
async def build_commit_prompt() -> str
async def format_conventional_commit(commit_message: CommitMessage | CommitGroup) -> str
async def process_commit_plan(commit_plan: CommitPlan) -> None
async def generate_commit_guidelines() -> str  # For AI prompts
```

### CommitMessage.format()

Returns conventional commit string. Does NOT respect config - use `CommitService.format_conventional_commit()` for config-aware formatting.

## Testing Patterns

Tests use VCR cassettes for AI interactions:

- `tests/agent/cassettes/test_commit_agent/`
- `tests/e2e/cassettes/test_commit_command/`

Test fixtures in `tests/git/` cover:

- Diff generation with various change types
- Commit service formatting
- Git service operations
