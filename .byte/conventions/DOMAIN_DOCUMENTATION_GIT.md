---
name: git-domain
description: Domain documentation for src/byte/git - Git repository operations, conventional commits, and AI-powered commit message generation. Use when working with git integration, commit workflows, or version control features.
---

# Git Domain Documentation

## Domain Purpose

The `git` domain handles git repository operations and AI-powered conventional commit generation. It provides:

- Git repository status and file tracking
- Staged/unstaged change detection and management
- Conventional commit message formatting (type, scope, breaking changes, body)
- AI-driven commit message generation from diffs
- Multi-commit planning (commit plans) for logical grouping
- User interaction for commit approval and breaking change confirmation

## Key Components

### Services

**GitService** (`service/git_service.py`)

- Core git operations: staging, committing, diff generation
- Repository state management
- File change tracking (modified, untracked, staged)
- Usage: `git_service = app.make(GitService)`

**CommitService** (`service/commit_service.py`)

- Conventional commit formatting and validation
- Commit prompt building for AI agents
- Commit plan processing (multiple commits from single diff)
- Commit guideline generation for AI context
- Usage: `commit_service = app.make(CommitService)`

### Commands

**CommitCommand** (`command/commit_command.py`)

- Entry point: `/commit` command
- Orchestrates: staging → linting → AI generation → user approval → commit
- Supports both single commits and commit plans
- Integrates with `CoderAgent` for lint fixes, `CommitAgent` for single commits, `CommitPlanAgent` for multi-commit workflows

### Validators

**CommitValidator** (`validators/commit_validator.py`)

- Validates `CommitMessage` and `CommitPlan` objects
- Displays formatted commits to user for approval
- Collects user feedback for AI revision
- Returns `ValidationError` with context when rejected

### Data Models

**CommitMessage** (`schemas.py`)

```python
CommitMessage(
    type="feat",                    # Required: commit type
    scope="api",                    # Optional: contextual scope
    commit_message="add endpoint",  # Required: description
    breaking_change=False,          # Optional: breaking change flag
    breaking_change_message=None,   # Required if breaking_change=True
    body=None                       # Optional: detailed explanation
)
```

**CommitGroup** (`schemas.py`)

- Extends `CommitMessage` with `files: list[str]`
- Used in commit plans to group related changes
- Provides `format_with_files()` for display

**CommitPlan** (`schemas.py`)

```python
CommitPlan(
    commits=[
        CommitGroup(type="feat", commit_message="...", files=["a.py"]),
        CommitGroup(type="docs", commit_message="...", files=["README.md"])
    ]
)
```

## Configuration

**GitConfig** (`config.py`)

```python
config.git.enable_scopes = True              # Include scope in commits
config.git.enable_breaking_changes = True    # Detect breaking changes
config.git.enable_body = True                # Include commit body
config.git.scopes = ["api", "ui", "core"]    # Available scopes
config.git.max_description_length = 72       # Max chars for description
config.git.description_guidelines = []       # Custom guidelines
```

## Business Logic Patterns

### Commit Workflow

1. **Stage changes**: `await git_service.stage_changes()`
   - Detects unstaged/untracked files
   - Prompts user for confirmation
   - Stages all changes with `git add --all`

2. **Validate changes exist**: `diff = await git_service.get_diff()`
   - Returns empty list if no staged changes
   - Prevents empty commits

3. **Run linters** (optional):
   - Executes configured lint commands
   - Offers to fix via `CoderAgent` if failures
   - Re-stages after fixes

4. **Build AI prompt**: `prompt = await commit_service.build_commit_prompt()`
   - Extracts staged diff with boundaries
   - Formats file changes with metadata
   - Includes commit guidelines

5. **Generate commit message**:
   - Single commit: `CommitAgent` → `CommitMessage`
   - Commit plan: `CommitPlanAgent` → `CommitPlan`

6. **Validate with user**: `CommitValidator`
   - Displays formatted message(s)
   - Prompts for approval
   - Collects revision requests

7. **Execute commit**:
   - Single: `await git_service.commit(formatted_message)`
   - Plan: `await commit_service.process_commit_plan(plan)`

### Commit Plan Processing

```python
# Unstage all files
await git_service.reset()

# Iterate commit groups
for commit_group in commit_plan.commits:
    # Stage only files for this group
    for file_path in commit_group.files:
        if file_exists:
            await git_service.add(file_path)
        else:
            await git_service.remove(file_path)  # Handle deletions

    # Commit this group
    formatted = await commit_service.format_conventional_commit(commit_group)
    await git_service.commit(formatted)
```

### Diff Generation

`get_diff()` returns structured diff data:

```python
[
    {
        "file": "config.py",
        "change_type": "M",           # A=added, M=modified, D=deleted, R=renamed
        "diff": "unified diff content",  # None for binary/deleted files
        "msg": "modified: config.py",
        "is_renamed": False,
        "is_modified": True,
        "is_new": False,
        "is_deleted": False
    }
]
```

### Conventional Commit Formatting

**Format**: `<type>[optional scope][!]: <description>\n\n[optional body]\n\n[optional footer]`

**Normalization**:

- Lowercase first character of description
- Remove trailing period
- Add `!` suffix for breaking changes (if confirmed)
- Add `BREAKING CHANGE:` footer if message provided

**Config-driven inclusion**:

```python
# Scope only if enabled AND present
if config.git.enable_scopes and commit_message.scope:
    header += f"({commit_message.scope})"

# Body only if enabled AND present
if config.git.enable_body and commit_message.body:
    message_parts.extend(["", commit_message.body])

# Breaking changes only if enabled
if config.git.enable_breaking_changes and commit_message.breaking_change:
    # Prompt user for confirmation
    confirmed = await self.prompt_for_confirmation(...)
    if confirmed:
        header += "!"
```

## API Contracts

### GitService

```python
# Get repository instance
repo = await git_service.get_repo() -> git.Repo

# Get changed files
files = await git_service.get_changed_files(include_untracked=True) -> List[Path]

# Stage operations
await git_service.stage_changes(force=False)  # Prompts user
await git_service.add("file.py")
await git_service.remove("deleted.py")
await git_service.reset("file.py")  # Unstage specific
await git_service.reset()           # Unstage all

# Commit
await git_service.commit("feat: add feature")

# Get diff
diff_data = await git_service.get_diff() -> List[dict]
```

### CommitService

```python
# Build AI prompt from staged changes
prompt = await commit_service.build_commit_prompt() -> str

# Format commit message
formatted = await commit_service.format_conventional_commit(commit_message) -> str

# Process commit plan
await commit_service.process_commit_plan(commit_plan)

# Generate guidelines for AI
guidelines = await commit_service.generate_commit_guidelines() -> str
```

## Integration Points

### With Agent Domain

- `CommitAgent`: Generates single `CommitMessage` from diff
- `CommitPlanAgent`: Generates `CommitPlan` with multiple `CommitGroup`s
- `CoderAgent`: Fixes lint errors before commit
- Uses `CommitValidator` for user approval loop

### With Lint Domain

- Runs `LintService` after staging
- Displays lint results summary
- Offers to fix via `CoderAgent` if failures
- Re-stages changes after fixes

### With CLI Domain

- Uses `InteractionService` for user prompts (via `UserInteractive` mixin)
- Displays panels/warnings via `Console`
- Integrates with command registry

### With Files Domain

- Uses `root_path()` to resolve file paths
- Checks file existence before staging/removing

## Domain-Specific Patterns

### Boundary-Based Prompt Formatting

```python
from byte.support import Boundary, BoundaryType

# Wrap diff sections
diff_section.append(
    Boundary.open(
        BoundaryType.CONTEXT,
        meta={"type": "Diff", "change_type": "M", "file": "config.py"}
    )
)
diff_section.append(diff_content)
diff_section.append(Boundary.close(BoundaryType.CONTEXT))

# Wrap rules for AI
commit_guidelines.append(
    Boundary.open(BoundaryType.RULES, meta={"type": "Allowed Commit Types"})
)
commit_guidelines.append(types_list)
commit_guidelines.append(Boundary.close(BoundaryType.RULES))
```

### UserInteractive Mixin

Services inherit `UserInteractive` for consistent prompting:

```python
class CommitService(Service, UserInteractive):
    async def format_conventional_commit(self, commit_message):
        confirmed = await self.prompt_for_confirmation(
            "This commit is marked as a breaking change. Confirm?",
            default=True
        )
```

### Error Handling in Commits

```python
while continue_commit:
    try:
        commit = self._repo.index.commit(commit_message)
        console.print_success_panel(...)
        continue_commit = False
    except Exception as e:
        console.print_error_panel(f"Failed to create commit: {e}")
        retry = await self.prompt_for_confirmation("Stage changes and try again?")
        if retry:
            # Re-stage originally staged files
            for file_path in staged_files:
                await self.add(file_path) if exists else await self.remove(file_path)
        else:
            continue_commit = False
```

### Commit Types Dictionary

```python
COMMIT_TYPES = {
    "feat": "Commits that add or remove a new feature to the API or UI",
    "fix": "Commits that fix an API or UI bug of a preceded feat commit",
    "refactor": "Commits that rewrite/restructure code without changing API or UI behaviour",
    "perf": "Commits that improve performance (special refactor commits)",
    "style": "Commits that do not affect meaning (white-space, formatting, etc)",
    "test": "Commits that add missing tests or correct existing tests",
    "build": "Commits that affect build components (build tool, CI, dependencies, etc)",
    "ops": "Commits that affect operational components (infrastructure, deployment, etc)",
    "docs": "Commits that affect documentation only",
    "chore": "Commits that represent tasks (initial commit, modifying .gitignore, etc)",
}
```

## Testing Conventions

- Use `create_test_file()` helper for file creation
- Mock `prompt_for_confirmation` to avoid blocking tests
- Use `@pytest.mark.vcr` for agent integration tests
- Verify commit messages in repo history: `repo.head.commit.message`
- Test config-driven behavior by modifying `config.git.*`
