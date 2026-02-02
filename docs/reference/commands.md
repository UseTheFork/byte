# Commands

Byte provides a comprehensive set of commands for interacting with your codebase, managing context, and controlling the AI assistant. Commands are organized by category for easy reference.

---


## System

`!<command>` - Execute a shell command and optionally add output to conversation context


## Agent

### `/ask`

```
usage: ask ...

Ask the AI agent a question or request assistance

positional arguments:
  ask_query  The user's question or query text

```

### `/convention`

```
usage: convention

Generate convention documents by analyzing codebase patterns and saving them
to the conventions directory

```

### `/research`

```
usage: research ...

Execute research agent to gather codebase insights, analyze patterns, and save
detailed findings to session context for other agents

positional arguments:
  research_query  The research query or question to investigate

```


## Clipboard

### `/copy`

```
usage: copy [--type {message,block}]

Copy code blocks from message history to clipboard

options:
  --type {message,block}
                        Filter code blocks by type (message or block)

```

### `/copy:drop`

```
usage: copy:drop [--type {message,block}]

Clear code blocks from the clipboard session

options:
  --type {message,block}
                        Filter code blocks by type (message or block)

```


## Config

### `/config:agent`

```
usage: config:agent agent

Configure agent-specific settings

positional arguments:
  agent  Name of the agent to configure

```


## Files

### `/add`

```
usage: add file_path

Add file to context as editable

positional arguments:
  file_path  Path to file

```

### `/drop`

```
usage: drop file_path

Remove file from context

positional arguments:
  file_path  Path to file

```

### `/ls`

```
usage: ls

List all files currently in the AI context

```

### `/read-only`

```
usage: read-only file_path

Add file to context as read-only

positional arguments:
  file_path  Path to file

```

### `/reload`

```
usage: reload

Reload project file discovery cache

```

### `/switch`

```
usage: switch file_path

Switch file mode between editable and read-only

positional arguments:
  file_path  Path to file

```


## General

### `/commit`

```
usage: commit

Create an AI-powered git commit with automatic staging and linting

```

### `/exit`

```
usage: exit

Exit the Byte application gracefully

```

### `/lint`

```
usage: lint

Run configured linters on changed files or current context

```

### `/preset`

```
usage: preset [--should-not-clear-history] [--should-not-clear-files]
              [--silent]
              preset_id

Load a predefined preset configuration with files and conventions

positional arguments:
  preset_id             ID of the preset to load

options:
  --should-not-clear-history
                        Do not clear conversation history before loading
                        preset
  --should-not-clear-files
                        Do not clear file context before loading preset
  --silent              Run silently without prompting for confirmations

```

### `/preset:save`

```
usage: preset:save

Save the current context as a preset configuration

```


## Memory

### `/clear`

```
usage: clear

Clear conversation history and start a new thread

```

### `/reset`

```
usage: reset

Reset conversation history and clear file context completely

```

### `/show`

```
usage: show

Display the current conversation history and context

```

### `/undo`

```
usage: undo

Undo the last conversation step by removing the most recent human message and
all subsequent agent responses from the current thread

```


## Session Context

### `/ctx:drop`

```
usage: ctx:drop file_path

Remove items from session context to clean up and reduce noise, improving AI
focus on current task

positional arguments:
  file_path  Path to file

```

### `/ctx:file`

```
usage: ctx:file file_path

Read a file from disk and add its contents to the session context, making it
available to the AI for reference during the conversation

positional arguments:
  file_path  Path to file

```

### `/ctx:ls`

```
usage: ctx:ls

List all session context items

```

### `/web`

```
usage: web url

Fetch webpage using headless Chrome, convert HTML to markdown, display for
review, and optionally add to LLM context

positional arguments:
  url  URL to scrape

```

