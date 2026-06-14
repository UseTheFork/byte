# Create AI-Powered Git Commits

**Category**: How-to Guide

This guide shows you how to use Byte's `/commit` command to create intelligent, well-formatted git commits. You'll learn how to configure commit behavior, understand the commit workflow, and review AI-generated commit messages before committing.

## Prerequisites

- Byte installed on your system
- A git repository initialized in your project
- Linting configured (see [Configure Linting](configuring-linting.md)) - commits validate code with your linters before finalizing
- A `.byte/config.jsonc` file (created during initialization)

## Step 1: Configure Git Behavior

Git behavior is controlled in `.byte/config.jsonc` under the `git` key. Open your config and add or update the git section:

```jsonc
{
  "git": {
    "enable_scopes": false,
    "enable_breaking_changes": false,
    "enable_body": true,
    "scopes": ["api", "auth", "cli", "config", "core", "db", "deps", "docs", "test", "ui"],
    "description_guidelines": [],
    "max_description_length": 72,
  },
}
```

### Configuration Options

**`enable_scopes`** - Whether to include optional scopes in commit messages. If `true`, the Commit Agent will ask you to select a scope from the `scopes` list. Default: `false`.

**`enable_breaking_changes`** - Whether to detect and flag breaking changes. If `true`, the Commit Agent will ask for confirmation when a commit is marked as breaking. Default: `false`.

**`enable_body`** - Whether to include an optional body section that explains the _why_ behind the change. Default: `true`.

**`scopes`** - An array of allowed scope values. Used only if `enable_scopes` is `true`. Examples: `api`, `auth`, `cli`, `docs`, `test`. Define scopes that match your project's logical domains.

**`description_guidelines`** - An array of custom guidelines for commit descriptions. These are passed to the Commit Agent to influence message quality. Leave empty for default behavior. Example: `["Use past tense for consistency", "Reference ticket numbers when applicable"]`.

**`max_description_length`** - Maximum character length for the commit description line (the first line after the type and scope). Default: 72. Conventional Commits recommends 50–72 characters.

### Example: Strict Conventional Commits

```jsonc
{
  "git": {
    "enable_scopes": true,
    "enable_breaking_changes": true,
    "enable_body": true,
    "scopes": ["api", "auth", "db", "ui"],
    "description_guidelines": ["Use imperative mood: 'add' not 'added'", "Reference issue numbers: 'fixes #123'"],
    "max_description_length": 72,
  },
}
```

### Example: Minimal Configuration

```jsonc
{
  "git": {
    "enable_scopes": false,
    "enable_breaking_changes": false,
    "enable_body": false,
  },
}
```

## Step 2: Understand the Commit Workflow

When you run `/commit`, Byte executes a three-stage workflow:

### Stage 1: Staging and Validation

Byte stages all changes in your working directory and validates that staged changes exist. If nothing is staged, the command exits early - no empty commits allowed.

### Stage 2: Linting

If linting is enabled, Byte runs your configured linters on the staged files and reports any errors. This ensures you're committing code that passes your project's quality standards.

### Stage 3: Commit Workflow (Analysis → Commit)

The Commit Agent analyzes the staged changes and generates an intelligent commit message:

1. **Analysis Phase** - The Commit Agent reviews your diffs and creates a SHORT list of observations (1–5 bullets) about what changed.

2. **Commit Phase** - Using those observations, the Commit Agent generates a commit message following conventional commit standards. The message includes:
   - **Type** (e.g., `feat`, `fix`, `docs`, `test`, `refactor`)
   - **Optional Scope** (if enabled in config)
   - **Description** - A clear, imperative-mood summary of the change
   - **Optional Body** (if enabled in config) - Why the change was made, not what was changed
   - **Optional Breaking Change Footer** (if marked as breaking)

## Step 3: Understand Conventional Commit Format

Byte generates commits following the Conventional Commits specification. Understanding the format helps you work effectively with the generated message.

### The Format

```
<type>[optional scope][!]: <description>

[optional body]

[optional BREAKING CHANGE footer]
```

### Type

The type categorizes the change:

- **`feat`** - A new feature for users
- **`fix`** - A bug fix for users
- **`docs`** - Documentation-only changes
- **`test`** - Adding or updating tests
- **`refactor`** - Code changes that neither fix bugs nor add features
- **`perf`** - Performance improvements
- **`chore`** - Changes to build scripts, dependencies, or tooling
- **`ci`** - Changes to CI/CD configuration

### Scope (Optional)

If scopes are enabled, a scope provides additional context. Examples: `(api)`, `(auth)`, `(database)`. The scope narrows the type to a specific part of your codebase.

### Description

A one-line imperative statement summarizing the change. Always use lowercase, never end with a period, and keep it under the configured `max_description_length` (default 72 characters).

**Good:**

- `add user authentication to admin panel`
- `fix off-by-one error in pagination logic`
- `refactor database connection pooling`

**Avoid:**

- `Added user authentication` (use imperative mood)
- `This commit adds user authentication to the admin panel which previously didn't have it and now does` (too long)
- `Add user authentication.` (no trailing period)

### Body (Optional)

Explains _why_ the change was made, not _what_ was changed (the diff shows that). Written in imperative, present tense. Use this when the description alone doesn't fully convey the motivation.

**Example:**

```
fix: correct user role permission check

The previous implementation only checked the admin role and ignored
custom role assignments. This prevented users with custom roles from
accessing protected endpoints even when explicitly granted permission.

This fix loads the full role hierarchy from the database and evaluates
all assigned roles, ensuring permission checks are comprehensive.
```

### Breaking Change Footer (Optional)

If a change breaks backward compatibility, add a footer:

```
BREAKING CHANGE: Authentication now requires the new token format.
Clients using the old format will receive a 401 Unauthorized response.
```

If `enable_breaking_changes` is true in your config, the Commit Agent asks for confirmation before marking a commit as breaking.

### Examples

**Simple feature:**

```
feat: add dark mode toggle to settings
```

**Fix with scope:**

```
fix(auth): resolve session timeout on refresh
```

**Breaking change:**

```
feat!: restructure API response format for consistency

BREAKING CHANGE: The /api/users endpoint now returns a 'data' wrapper
object. Clients must update their response parsing logic.
```

**Full example with body and scope:**

```
refactor(database): optimize connection pool configuration

The previous pool settings were conservative and caused connection
timeouts under moderate load. Profiling showed we were frequently
hitting the pool limit during peak usage.

This change increases the pool size to 25 connections and enables
connection reuse, reducing latency by ~30% in benchmarks.
```

## Step 4: Run the Commit Command

To create a commit, type:

```bash
/commit
```

Byte will:

1. **Stage all changes** in your working directory
2. **Validate** that changes exist (no empty commits)
3. **Run linting** on staged files (if enabled)
4. **Launch the Commit Workflow**:
   - The Commit Agent analyzes your diffs
   - A commit message is generated and presented to you
5. **Pause for approval** - you see the generated message and decide

That's it. No additional arguments needed. The entire workflow is guided and interactive.

## Step 5: Review and Approve the Generated Commit

When the Commit Agent finishes generating the message, you'll see a panel displaying the full commit. You have two options:

**Option 1: Approve the Commit**

If the message looks good, confirm it. Byte commits the message immediately and returns to the prompt.

**Option 2: Request Changes**

If something needs adjusting, tell Byte what to change. For example:

- `"The description should mention the API endpoint change"`
- `"Add a body explaining the performance impact"`
- `"Mark this as a breaking change"`

Byte will revise the message based on your feedback and present it again for approval. You can request changes as many times as needed until the message is exactly right.

## Step 6: Verify Your Commit

After approval, Byte commits the message to your repository. To confirm the commit was created, check your recent commits:

```bash
git log --oneline -5
```

You should see your new commit at the top with the formatted message.

## Common Workflows

### Scenario 1: Quick Bugfix with Scopes Enabled

```jsonc
{
  "git": {
    "enable_scopes": true,
    "scopes": ["api", "auth", "ui"],
  },
}
```

Run `/commit`. The Commit Agent analyzes your changes and generates:

```
fix(auth): reset user session on password change
```

You approve it. Done.

### Scenario 2: Feature with Breaking Change

```jsonc
{
  "git": {
    "enable_breaking_changes": true,
    "enable_body": true,
  },
}
```

Run `/commit`. The Commit Agent detects that your change breaks backward compatibility and marks it accordingly:

```
feat!: redesign authentication API

The login endpoint now expects JWT tokens in the Authorization header
instead of cookies. Clients using the old cookie-based auth will need
to update their integration.
```

You approve it. Done.

### Scenario 3: Customizing the Message

Run `/commit`. The generated message appears:

```
refactor: clean up database queries
```

You request: `"The description should mention performance improvements"`. The Commit Agent revises it:

```
refactor: optimize database query performance
```

You approve it. Done.

## Next Steps

Now that you understand how to create commits, explore how commits integrate with the broader development workflow:

- **Configure Linting** - Ensure your commits always pass quality checks
- **Manage the Constitution** - Set coding standards that guide the Commit Agent's message generation

For deeper understanding of how conventional commits work and why they're valuable, see the Explanation section.
