# Files

## File Modes Explained

Byte uses two file modes to control AI permissions:

### Editable Mode

- **Command**: `/add`
- **Permissions**: AI can read content and propose changes via SEARCH/REPLACE blocks
- **Use case**: Files you're actively developing
- **In prompt**: Listed under "## EDITABLE FILES (can be modified):"

### Read-Only Mode

- **Command**: `/read-only`
- **Permissions**: AI can read content for context but cannot propose changes
- **Use case**: Reference files, documentation, configuration, test examples
- **In prompt**: Listed under "## READ-ONLY FILES (for reference only):"

**How modes affect AI behavior:**

When you add files to context, Byte generates a structured prompt that clearly indicates which files can be edited:

```markdown
# Here are the files in the current context:

## READ-ONLY FILES (for reference only):

Any edits to these files will be rejected

config.yaml:
\`\`\`yaml
model: sonnet
\`\`\`

## EDITABLE FILES (can be modified):

src/main.py:
\`\`\`python
def main():
pass
\`\`\`
```

This explicit labeling ensures the AI understands its permissions for each file.

**File mode enforcement:**

File modes are actively enforced when AI proposes changes. Before any SEARCH/REPLACE block is applied:

1. Byte verifies the target file is in the editable context
2. Read-only files are protected - any attempted edits are rejected
3. Files not in context cannot be modified
4. Users see clear error messages if the AI attempts unauthorized modifications

This double-layer protection (prompt instruction + runtime validation) ensures your read-only files remain safe from accidental changes.

---

## File Discovery System

Byte's File Discovery Service scans your project on boot to build a fast, indexed cache of all valid project files.

**What gets discovered:**

- All files in your project directory
- Files tracked by git (committed, staged, or untracked but not ignored)
- Files not matching `.gitignore` patterns
- Files not matching custom ignore patterns in `config.yaml`

**What gets excluded:**

- Files in `.gitignore`
- Common directories: `.venv/`, `node_modules/`, `__pycache__/`, `.ruff_cache/`
- The `.byte/` directory itself
- Custom patterns from your configuration

**Discovery on boot:**
![boot screen](./../images/boot_screen.png)

**Custom ignore patterns:**

Edit `.byte/config.yaml` to add project-specific exclusions:

```yaml
files:
  ignore:
    - "*.log"
    - "build/**"
    - "dist/**"
    - ".mypy_cache"
```

---

## Best Practices

### 1. Start with Minimal Context

Begin with only the files you're actively working on:

```bash
> /add src/auth.py src/models/user.py
```

**Why:** Smaller context leads to faster responses and more focused suggestions.

### 2. Use Read-Only for References

Add related code, tests, or documentation as read-only:

```bash
> /read-only tests/test_auth.py
> /read-only docs/authentication.md
> /read-only config/auth_config.yaml
```

**Why:** Provides context without risking unwanted changes.

### 3. Leverage Glob Patterns

Add related files together:

```bash
> /add src/auth/*.py        # All auth module files
> /read-only tests/**/*.py  # All tests as reference
```

**Why:** Faster than adding files one by one.

### 4. Clear Between Tasks

Start fresh when switching to unrelated work:

```bash
> /drop src/**/*
> /add src/billing/*.py
```

**Why:** Reduces context noise and improves AI focus.

### 5. Check Context Regularly

Use `/ls` before making requests:

```bash
> /ls
# Review what's in context
> Now refactor the authentication flow
```

**Why:** Ensures AI has the right files before processing requests.

### 6. Use AI Comments for Common Tasks

Instead of typing commands, use AI comments in your code:

```python
# AI: Add input validation
# AI: Write unit tests for this function
# AI? Is there a more efficient algorithm?
```

**Why:** Keeps your workflow in the editor, faster iteration.

---

## Common Issues

### File Not Found

**Error:**

```
Failed to add src/main.py (file not found, not readable, or is already in context)
```

**Causes:**

1. File doesn't exist or path is incorrect
2. File is ignored by `.gitignore`
3. File is outside project root
4. File is already in context

**Solutions:**

```bash
# Check file exists
$ ls src/main.py

# Check if gitignored
$ git check-ignore src/main.py

# Use relative path from project root
> /add src/main.py  # not /absolute/path/to/src/main.py

# Check if already added
> /ls
```

---

## Integration with Other Features

### With Linting

Files in context are automatically linted after AI makes changes (if enabled):

```bash
> /add src/main.py
> Fix the login bug

# AI proposes changes
# Changes are applied
# Linter runs automatically
# Results displayed
```

See [Linting Configuration](../configuration.md#linting) for details.

---

## Related Documentation

- **[Quick Start Guide](../quickstart.md)** - Initial setup and first session
- **[Configuration](../configuration.md)** - Customize file discovery and ignore patterns
- **[Linting](../linting.md)** - Automatic code quality checks
- **[Git Integration](../git.md)** - Version control workflows
- **[MCP Servers](../mcp.md)** - Extended tool capabilities

---

**Next:** Learn about [Session Commands](session.md) to manage your conversation history.
