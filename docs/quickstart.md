# Quick Start Guide

Get started with Byte in minutes. This guide walks you through your first session with Byte, a human-in-the-loop flow coding agent.

## Prerequisites

Before running Byte, ensure you have:

1. **Git repository**: Byte must be run inside a git repository
2. **AI API key**: At least one of the following environment variables set:
   - `ANTHROPIC_API_KEY` (for Claude models)
   - `GEMINI_API_KEY` (for Google Gemini)
   - `OPENAI_API_KEY` (for OpenAI models)

## Initial Setup

### 1. Navigate to Your Project

Byte must be run from within a git repository:

```bash
cd /path/to/your/project

# If not already a git repo, initialize one
git init
```

### 2. Set Your API Key

Create a `.env` file in your project root or export the environment variable:

```bash
# Using .env file (recommended)
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Or export directly
export ANTHROPIC_API_KEY=your-key-here
```

### 3. Run Byte

Simply run Byte from your project directory:

```bash
byte
```

On first run, Byte will automatically:

- Create a `.byte/` directory in your project root
- Generate a default `config.yaml` configuration file
- Display a welcome message with setup confirmation

## Understanding the `.byte` Directory

Byte creates a `.byte/` directory in your project root containing:

- **`config.yaml`**: Configuration settings for Byte behavior
- **Cache files**: Temporary data and performance optimizations
- **Chat history**: Records of your interactions with the AI agent

### Add to `.gitignore`

Since `.byte/` contains local cache and history, add it to your `.gitignore`:

```bash
echo ".byte/" >> .gitignore
```

## Configuration

After first run, you'll find `config.yaml` in `.byte/`. Key settings include:

```yaml
# Model selection
model: sonnet # Claude Sonnet by default

# Linting integration
lint:
  enabled: true

# File handling
files:
  ignore:
    - .ruff_cache
    - .venv
    - node_modules
    - __pycache__
```

Edit this file to customize Byte's behavior. See [Configuration](configuration.md) for detailed options.

## Your First Session

Once Byte is running, you'll see an interactive prompt. Try these commands:

```
# Ask Byte to help with a task
> Can you help me refactor the login function?

# Add files to context
> /add src/auth.py

# Review what files are in context
> /files

# Get help
> /help
```

## Next Steps

- Learn about [available commands](commands.md) and workflows
- Configure [linting integration](configuration.md#linting) for your project
- Explore [file management](files.md) and context handling
- Set up [MCP servers](mcp.md) for extended capabilities

## Example Workflow

Here's a typical session with Byte:

```bash
# Start Byte in your project
cd ~/projects/myapp
byte

# Add files you want to work with
> /add src/main.py src/utils.py

# Ask for help
> I need to add error handling to the process_data function

# Byte will suggest changes, review them
> /approve

# Continue the conversation
> Now let's add logging to track when errors occur
```

Byte keeps you in control with human-in-the-loop approvals for all code changes.
