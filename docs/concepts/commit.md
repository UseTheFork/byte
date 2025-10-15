# Commit

Byte's commit system uses AI to generate meaningful commit messages by analyzing your staged changes. It automates the entire commit workflow - staging files, running linters, generating commit messages, and handling git operations - while keeping you in control at each step.

![Commit process showing staging, linting, and message generation](../images/commit.svg)

---

## Quick Start

Create an AI-powered commit:

```
> /commit
```

Byte will:

1. Stage all changed files (with confirmation)
2. Run configured linters on changed files
3. Analyze the git diff with AI
4. Generate a descriptive commit message
5. Create the commit with the generated message

---

## How It Works

### 1. Staging Changes

The commit process begins by staging your changes:

```
Found 3 unstaged changes:
  • src/main.py (modified)
  • tests/test_main.py (new)
  • README.md (modified)

Add unstaged changes to commit? (Y/n):
```

If you confirm, Byte runs `git add --all` to stage the files.

**Empty commits are prevented** - if no changes are staged, the process stops early:

```
No staged changes to commit.
```

### 2. Linting Changed Files

After staging, Byte automatically runs your configured linters on the changed files:

```
Running linters on changed files...
✓ ruff format (3 files)
✓ ruff check (3 files)
```

This ensures code quality before committing. If linting fails, you can:

- Fix issues manually and run `/commit` again
- Use AI-assisted fixes (see [Linting concept](lint.md))
- Skip linting by disabling it in config

### 3. AI Message Generation

Byte extracts the staged diff and sends it to the commit agent:

```bash
$ git diff --cached
```

The AI analyzes:

- What files changed
- What code was added/removed/modified
- The nature of the changes (feature, fix, refactor, etc.)

Based on this analysis, it generates a commit message following conventional commit format:

```
feat: add user authentication service

- Implement JWT token generation and validation
- Add login and logout endpoints
- Include unit tests for auth service
```

### 4. Creating the Commit

The generated message is used to create the commit:

```
┌─ Commit Created ─────────────────────┐
│ (a3f5b2) feat: add user auth service │
└──────────────────────────────────────┘
```

If the commit fails (e.g., pre-commit hooks fail), you'll be prompted:

```
┌─ Commit Failed ───────────────────────┐
│ Failed to create commit: pre-commit   │
│ hook returned non-zero exit code      │
└───────────────────────────────────────┘

Stage changes and try again? (Y/n):
```

---

## Configuration

### Linting Integration

Control linting behavior via `.byte/config.yaml`:

```yaml
lint:
  enable: true # Disable to skip linting during commits
  commands:
    - command: "ruff format"
      extensions: [".py"]
```

See [Linting concept](lint.md) for detailed configuration.

### Git Integration

The commit command respects your git configuration:

- **User name/email** - Uses your git config values
- **Hooks** - Pre-commit and commit-msg hooks run normally
- **Signing** - GPG signing works if configured

---

## Commit Message Format

The AI generates messages following conventional commit conventions:

### Structure

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

Common commit types the AI uses:

- **feat** - New feature
- **fix** - Bug fix
- **docs** - Documentation changes
- **style** - Code style changes (formatting, whitespace)
- **refactor** - Code restructuring without behavior change
- **perf** - Performance improvements
- **test** - Test additions or modifications
- **chore** - Build process, tooling, dependencies

### Examples

**Simple feature:**

```
feat: add password reset functionality
```

**Bug fix with scope:**

```
fix(auth): prevent token expiration race condition
```

**Breaking change:**

```
feat!: redesign authentication API

BREAKING CHANGE: AuthService.login() now returns a Promise
instead of synchronous result. Update all callers to use await.
```

---

## Best Practices

### Stage Incrementally

Create focused commits by staging related changes:

```bash
$ git add src/auth/*.py tests/auth/
$ byte
> /commit
```

This produces more meaningful commit messages than staging everything at once.

### Review Before Committing

The AI shows you the generated message before committing. Review it and:

- Accept if it accurately describes the changes
- Edit manually if needed (`git commit --amend`)
- Cancel and refine your changes if the message seems off

### Lint Before Commit

Keep linting enabled to catch issues early:

```yaml
lint:
  enable: true # Recommended
```

This prevents committing code that fails quality checks.

### Small, Atomic Commits

Break large changes into smaller commits:

```
❌ feat: complete user management system (50 files)
✓ feat: add user model and repository
✓ feat: add user authentication endpoints
✓ feat: add user profile management
```

The AI generates better messages for focused changes.

---

## Implementation Details

### Commit Agent

The commit command uses the `CommitAgent`, a specialized AI agent that:

- Receives the git diff as input
- Analyzes code changes and context
- Generates structured commit messages
- Returns the message for git commit

**Agent configuration:**

```python
commit_agent = await self.make(CommitAgent)
commit_message: dict = await commit_agent.execute(
    request={"messages": [("user", staged_diff)]},
    display_mode="thinking"
)
```

### Git Service

The `GitService` handles git operations:

- **`stage_changes()`** - Detects and stages unstaged files
- **`get_changed_files()`** - Lists modified files for linting
- **`commit(message)`** - Creates the commit with error handling

**Error recovery:**

```python
async def commit(self, commit_message: str) -> None:
    try:
        commit = self._repo.index.commit(commit_message)
        # Success
    except Exception as e:
        # Prompt to stage and retry
        if await self.prompt_for_confirmation("Stage changes and try again?"):
            await self.stage_changes()
```

### Workflow Integration

The commit command orchestrates multiple services:

1. **GitService** - Stage changes and extract diff
2. **LintService** - Validate code quality
3. **CommitAgent** - Generate commit message
4. **GitService** - Create the commit

This separation of concerns makes each component testable and reusable.

---

## Troubleshooting

### "No staged changes to commit"

**Cause:** No files were staged or all changes were already committed.

**Solution:**

- Make changes to files
- Run `/commit` again (it will offer to stage)
- Or manually stage: `git add <files>`

### Linting Failures Block Commit

**Cause:** Configured linters found issues in changed files.

**Solution:**

- Fix lint errors manually
- Use AI-assisted fixes (prompted after linting)
- Temporarily disable linting in config

### Commit Message Doesn't Match Changes

**Cause:** The AI misunderstood the context or changes were too broad.

**Solution:**

- Stage smaller, more focused changes
- Add conventions describing your commit style (see [Conventions](conventions.md))
- Edit the commit message after creation: `git commit --amend`

### Pre-commit Hooks Fail

**Cause:** Your project's pre-commit hooks rejected the commit.

**Solution:**

- The commit command offers to stage and retry
- Fix issues identified by hooks
- Update hooks if they're too strict

---

## Related Concepts

- [Linting](lint.md) - Automatic code quality checks before commits
- [File Context](file-context.md) - Managing which files are visible to the AI
- [Conventions](conventions.md) - Define commit message style preferences

---

## Related Commands

**View commit history:**

```bash
$ git log --oneline
```

**Amend last commit message:**

```bash
$ git commit --amend
```

**Review staged changes:**

```bash
$ git diff --cached
```

**Unstage files:**

```bash
$ git restore --staged <file>
```
