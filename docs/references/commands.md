## Agent Commands

### /ask

Ask the AI agent a question or request assistance

**Method name**: `ask`

**Parameters**:

- `ask_query` (string, required) — The user's question or query text (takes all remaining arguments)

**Usage**: `/ask` or `/ask <args>`

### /coder

Ask the AI agent to perform a code operation

**Method name**: `coder`

**Parameters**:

- `coder_request` (string, required) — The user's request (takes all remaining arguments)

**Usage**: `/coder` or `/coder <args>`

### /constitution

Ask the AI agent a question or request assistance

**Method name**: `constitution`

**Parameters**:

- `constitution_query` (string, required) — The user's question or query text (takes all remaining arguments)

**Usage**: `/constitution` or `/constitution <args>`

### /docs

Ask the AI agent to perform a documentation operation

**Method name**: `docs`

**Parameters**:

- `documentation_request` (string, required) — The user's request (takes all remaining arguments)

**Usage**: `/docs` or `/docs <args>`

### /init

Initialize the project constitution

**Method name**: `init`

**Parameters**:

None

**Usage**: `/init`

### /research

Ask the AI agent a question or request assistance

**Method name**: `research`

**Parameters**:

- `research_query` (string, required) — The user's question or query text (takes all remaining arguments)

**Usage**: `/research` or `/research <args>`

### /skill

Have an agent create a new skill

**Method name**: `skill`

**Parameters**:

- `skill_query` (string, required) — The user's query to geneate the skill for (takes all remaining arguments)

**Usage**: `/skill` or `/skill <args>`

### /spec:execute

Execute or continue executing a spec

**Method name**: `spec:execute`

**Parameters**:

- `spec` (string, required) — The task id

**Usage**: `/spec:execute` or `/spec:execute <args>`

### /spec:init

Have an agent create a new spec

**Method name**: `spec:init`

**Parameters**:

- `spec_query` (string, required) — The user's query to generate the spec for (takes all remaining arguments)

**Usage**: `/spec:init` or `/spec:init <args>`

### /spec:quick

Have an agent create a new quick spec

**Method name**: `spec:quick`

**Parameters**:

- `spec_query` (string, required) — The user's query to generate the spec for (takes all remaining arguments)

**Usage**: `/spec:quick` or `/spec:quick <args>`

### /spec:refractor

Have an agent create a new refactoring spec

**Method name**: `spec:refractor`

**Parameters**:

- `refractor_query` (string, required) — The user's query to generate the spec for (takes all remaining arguments)

**Usage**: `/spec:refractor` or `/spec:refractor <args>`


## Files Commands

### /add

Add file to context as editable

**Method name**: `add`

**Parameters**:

- `file_path` (string, required) — Path to file

**Usage**: `/add` or `/add <args>`

### /drop

Remove file from context

**Method name**: `drop`

**Parameters**:

- `file_path` (string, required) — Path to file

**Usage**: `/drop` or `/drop <args>`

### /ls

List all files currently in the AI context

**Method name**: `ls`

**Parameters**:

None

**Usage**: `/ls`

### /reload

Reload project file discovery cache

**Method name**: `reload`

**Parameters**:

None

**Usage**: `/reload`


## General Commands

### /commit

Create an AI-powered git commit with automatic staging and linting

**Method name**: `commit`

**Parameters**:

None

**Usage**: `/commit`

### /exit

Exit the Byte application gracefully

**Method name**: `exit`

**Parameters**:

None

**Usage**: `/exit`

### /lint

Run configured linters on changed files or current context

**Method name**: `lint`

**Parameters**:

None

**Usage**: `/lint`


## Memory Commands

### /clear

Clear conversation history and start a new thread

**Method name**: `clear`

**Parameters**:

None

**Usage**: `/clear`

### /reset

Reset conversation history and clear file context completely

**Method name**: `reset`

**Parameters**:

None

**Usage**: `/reset`

### /undo

Undo the last conversation step by removing the most recent human message and all subsequent agent responses from the current thread

**Method name**: `undo`

**Parameters**:

None

**Usage**: `/undo`


## Session Context Commands

### /context

Add a file or URL to session context. Automatically detects the type and handles appropriately.

**Method name**: `context`

**Parameters**:

- `target` (string, required) — Path to file or URL to add

**Usage**: `/context` or `/context <args>`

### /ctx:drop

Remove items from session context to clean up and reduce noise, improving AI focus on current task

**Method name**: `ctx:drop`

**Parameters**:

- `file_path` (string, optional) — Path to file (optional - if not provided, shows multiselect menu)

**Usage**: `/ctx:drop` or `/ctx:drop <args>`

### /ctx:file

Read a file from disk and add its contents to the session context, making it available to the AI for reference during the conversation

**Method name**: `ctx:file`

**Parameters**:

- `file_path` (string, required) — Path to file

**Usage**: `/ctx:file` or `/ctx:file <args>`

### /ctx:ls

List all session context items

**Method name**: `ctx:ls`

**Parameters**:

None

**Usage**: `/ctx:ls`

### /web

Fetch webpage using headless Chrome, convert HTML to markdown, display for review, and optionally add to LLM context

**Method name**: `web`

**Parameters**:

- `urls` (string, required) — One or more URLs to scrape (space, comma, or newline separated)

**Usage**: `/web` or `/web <args>`

