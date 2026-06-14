# Available Commands

**Category**: Explanation

This page lists all currently available commands. In the future, this list will be dynamically generated from the command registry, but for now it's manually maintained. Each command is documented with its name, category, purpose, and basic usage.

## Agent Commands

### /coder

Ask the AI agent to perform a code operation.

**Method name**: `coder`

**Parameters**:

- `request` (string, required) — The code operation request (takes all remaining arguments)

**Response**: Streaming output as the AI codes. Final response indicates completion.

**Notes**: Invokes the coder workflow, which coordinates planning, implementation, and validation. Output streams in real time. Works with files already added to context.

**Usage**: `/coder refactor the login handler to use async/await`

### /ask

Ask the AI a question.

**Method name**: `ask`

**Parameters**:

- `question` (string, required) — Your question (takes all remaining arguments)

**Response**: Streaming response from the AI. Returns when the AI finishes answering.

**Notes**: A lightweight way to get information without triggering a full workflow. Useful for understanding code, asking for explanations, or quick clarifications.

**Usage**: `/ask explain how the gateway authentication works`

### /commit

Create AI-powered git commits.

**Method name**: `commit`

**Parameters**:

- `scope` (string, optional) — Scope or pattern for files to include

**Response**: AI-generated commit message and confirmation of the commit.

**Notes**: Analyzes staged changes and generates a well-structured commit message. Requires staged changes in git.

**Usage**: `/commit` or `/commit src/`

### /lint

Run linting on changed files.

**Method name**: `lint`

**Parameters**: None

**Response**: Linting results and fixes applied.

**Notes**: Runs configured linters on modified files. Can auto-fix many issues. Output shows what changed.

**Usage**: `/lint`

### /spec:init

Create a thorough spec with design exploration.

**Method name**: `spec:init`

**Parameters**:

- `topic` (string, required) — Feature or component to specify (takes all remaining arguments)
- `--design-exploration` (flag, optional) — Enable extensive design exploration phase

**Response**: Streaming spec generation. Writes `.byte/spec.md` with the final specification.

**Notes**: Invokes a multi-phase workflow: requirements gathering, design exploration (if enabled), implementation planning. Best for complex features.

**Usage**: `/spec:init --design-exploration authentication system` or `/spec:init cache invalidation`

### /spec:quick

Create a quick spec.

**Method name**: `spec:quick`

**Parameters**:

- `topic` (string, required) — Feature or component to specify (takes all remaining arguments)

**Response**: Streaming spec generation. Writes `.byte/spec.md` with the final specification.

**Notes**: Lightweight alternative to `spec:init`. Skips design exploration and focuses on implementation steps. Fast turnaround.

**Usage**: `/spec:quick add email validation`

### /spec:refactor

Create a refactoring spec.

**Method name**: `spec:refactor`

**Parameters**:

- `scope` (string, required) — Code section or file to refactor (takes all remaining arguments)

**Response**: Streaming spec generation. Writes `.byte/spec.md` with refactoring plan.

**Notes**: Specialized spec for refactoring work. Focuses on existing code, maintainability, and testing strategy.

**Usage**: `/spec:refactor the payment processing module`

### /spec:execute

Execute a spec's tasks.

**Method name**: `spec:execute`

**Parameters**:

- `spec_file` (string, optional) — Path to spec file. Defaults to `.byte/spec.md`

**Response**: Streaming execution output as each spec task runs.

**Notes**: Takes a previously generated specification and executes all tasks. Works with specs from any source.

**Usage**: `/spec:execute` or `/spec:execute my-custom-spec.md`

### /constitution

Modify the project constitution.

**Method name**: `constitution`

**Parameters**:

- `change` (string, required) — Description of the constitutional change (takes all remaining arguments)

**Response**: AI-generated amendment and confirmation.

**Notes**: Invokes a workflow to amend the project's constitution (principles, practices, standards). Changes are reviewed before being written.

**Usage**: `/constitution add a new principle about testing`

### /init

Initialize a new project.

**Method name**: `init`

**Parameters**:

- `project_type` (string, optional) — Type of project (default: auto-detect or prompt)

**Response**: Initialization output. Scaffolds project structure.

**Notes**: Sets up a new project: creates directories, installs templates, initializes version control, writes initial config.

**Usage**: `/init` or `/init python-fastapi`

### /skill

Create or manage skills.

**Method name**: `skill`

**Parameters**:

- `action` (string, required) — Action to perform: `create`, `list`, `remove`, `edit`
- `skill_name` (string, optional) — Name of the skill (required for `create`, `remove`, `edit`)

**Response**: Confirmation and output.

**Notes**: Skills are reusable AI instructions stored in `.byte/skills/`. Create custom skills to guide the AI on domain-specific tasks.

**Usage**: `/skill create my-testing-skill` or `/skill list` or `/skill remove old-skill`

## Context Commands

### /context

Add file or web content to session context.

**Method name**: `context`

**Parameters**:

- `source` (string, required) — File path or web URL to add

**Response**: Confirmation and summary of content added.

**Notes**: Intelligent dispatcher. Detects if the source is a file path or URL and delegates to the appropriate handler.

**Usage**: `/context src/main.py` or `/context https://example.com/docs`

### /ctx:file

Add a file to session context.

**Method name**: `ctx:file`

**Parameters**:

- `file_path` (string, required) — Relative or absolute path to the file

**Response**: Confirmation and file size/content summary.

**Notes**: Adds file contents to context without marking as editable. Useful for reference materials, examples, or read-only config files.

**Usage**: `/ctx:file README.md` or `/ctx:file docs/api.md`

### /ctx:drop

Remove items from session context.

**Method name**: `ctx:drop`

**Parameters**:

- `identifier` (string, required) — File path or context item ID to remove

**Response**: Confirmation of removal.

**Notes**: Removes a previously added context item. Does not affect files added via `/add`.

**Usage**: `/ctx:drop src/legacy.py` or `/ctx:drop web:https://example.com`

### /ctx:ls

List session context items.

**Method name**: `ctx:ls`

**Parameters**: None

**Response**: Formatted list of all context items with their types and sizes.

**Notes**: Shows both editable files (from `/add`) and reference context items (from `/context`, `/ctx:file`, `/web`).

**Usage**: `/ctx:ls`

### /web

Add web pages to session context.

**Method name**: `web`

**Parameters**:

- `url` (string, required) — Full or relative URL to fetch

**Response**: Confirmation and content summary.

**Notes**: Fetches and adds web page content to context. Useful for documentation, examples, or external references.

**Usage**: `/web https://docs.example.com/api` or `/web https://github.com/user/repo/blob/main/README.md`

## File Management Commands

### /add

Add a file to AI context as editable.

**Method name**: `add`

**Parameters**:

- `file_path` (string, required) — Relative or absolute path to the file

**Response**: Confirmation with file path and size.

**Notes**: Files added with `/add` are tracked by the file service and appear in all context summaries. The AI can modify editable files.

**Usage**: `/add src/main.py` or `/add config/settings.toml`

### /drop

Remove a file from AI context.

**Method name**: `drop`

**Parameters**:

- `file_path` (string, required) — Relative or absolute path to the file

**Response**: Confirmation with file path.

**Notes**: Once dropped, the file no longer appears in context summaries and the AI cannot modify it.

**Usage**: `/drop src/main.py` or `/drop config/legacy.toml`

