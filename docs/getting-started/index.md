# Getting Started

Get started with Byte in minutes. Byte is a human-in-the-loop AI coding agent that helps you build and refactor code through natural conversation.

---

## Prerequisites

Before running Byte, you need:

- **Git repository** - Byte operates inside a git repository
- **AI API key** - Set one of these environment variables:
  - `ANTHROPIC_API_KEY` for Claude models
  - `GEMINI_API_KEY` for Google Gemini
  - `OPENAI_API_KEY` for OpenAI models

---

## Quick Start

### Navigate to Your Project

Byte runs from within a git repository:

```bash
$ cd /path/to/your/project
$ git init  # If not already a git repo
```

### Set Your API Key

Create a `.env` file or export the environment variable:

```bash
$ echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

Or export directly:

```bash
$ export ANTHROPIC_API_KEY=your-key-here
```

### Run Byte

Launch Byte from your project directory:

```bash
$ byte
```

On first run, Byte automatically:

- Create a `.byte/` directory in your project root
- Generate a default `config.yaml` configuration file

---

## Understanding Configuration

Byte creates a `.byte/` directory containing:

- `config.yaml` - Configuration settings for Byte behavior
- Cache files - Temporary data and performance optimizations
- Chat history - Records of your interactions with the AI agent

!!! tip
Add `.byte/cache` to your `.gitignore` since it contains local cache and history.

---

## Next Steps

Now that you have Byte running, explore these topics:

- [Configuration](../configuration/index.md) - Customize Byte's behavior
- [Commands](../commands/index.md) - Learn all available commands
- [Workflows](../workflows/index.md) - Common development patterns
