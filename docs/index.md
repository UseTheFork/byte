# Byte

<p align="center"><img alt="Byte Logo" src="images/logo.svg" /></p>

A human-in-the-loop AI coding agent that keeps you in control.

---

## What is Byte?

Byte is a CLI coding agent designed for developers who want AI assistance without sacrificing control. Unlike autonomous agents that make multiple decisions and tool calls independently, Byte requires your approval for every decision.

**Key Features:**

- Review and confirm every change before it's applied
- See exactly what the agent modifies in your code
- Manage precisely what information the AI receives
- Slots into your existing development environment
- Structured prompts that adapt and evolve with each interaction
- Automatic linting, formatting, and testing without extra commands

---

## Design Philosophy

**Transparency First** - You see the complete prompt, not just your input. All interactions are logged for reference and debugging.

**Explicit Over Implicit** - Changes require approval. Context additions need confirmation. No surprises.

**Complementary, Not Replacement** - Byte enhances your workflow without replacing your tools or editor.

**Quality Over Quantity** - Better prompts produce better results. Byte prioritizes well-structured instructions over large context windows.

---

## Quick Start

Get started in three steps:

```bash
# Install with uv
$ uv tool install byte

# Navigate to your project
$ cd /path/to/your/project

# Run Byte
$ byte
```

See the [Installation Guide](getting-started/installation.md) for other installation methods including pip and Nix.

---

## Why This Approach?

### Human-in-the-Loop Design

Every decision and code change requires your confirmation. If you prefer agents that work autonomously, Byte isn't for you. If you value control and transparency, you'll appreciate the deliberate confirmation flow.

### Built for Experienced Developers

Designed for experienced developers who understand good design principles. This isn't a tool where you provide a specification and it builds the entire feature. Instead, Byte excels at small, incremental changes that keep you in control. Understanding when to refactor, how to structure code, and what constitutes good design remains your responsibility.

### Search/Replace Over Tools

Instead of giving the AI arbitrary tools, explicit Search/Replace blocks show you the exact changes before they happen, making it easy to cancel or modify the proposed work.

### Workflow Preservation

Your editor stays central to development. Whether you use Vim, VS Code, or Jetbrains, Byte complements your existing workflow as something you invoke when needed.

### Context Management

You control exactly what context the LLM receives:

- Add or remove files from the active context
- Monitor token usage and memory consumption
- Prevent context overflow with targeted information

### Intelligent Prompting

Structured prompts adapt with each turn:

- Previous Search/Replace blocks get removed to maintain focus
- Instructions follow clear markdown formatting
- Reduces "tunnel vision" where agents fixate on minor issues
- Full prompt visibility through logging for debugging

### Integrated Tooling

Linting, formatting, and testing run automatically after code changes are applied. Configure your tools once and they work seamlessly in the background without requiring agent interaction.

### Controlled MCP Integration

Model Context Protocol (MCP) tools are available but tightly controlled. Manually run tools or restrict which agents can access specific capabilities.

---

## Built With

Byte leverages modern Python tooling and AI frameworks:

- **uv** - Fast Python package management
- **LangChain** - AI framework for language models
- **LangGraph** - Graph-based agent workflows
- **Rich** - Beautiful terminal output
- **Prompt Toolkit** - Interactive command-line interfaces

---

## Inspiration

Byte draws inspiration from excellent projects in the coding agent space:

- [Aider](http://aider.chat/) - The pioneering CLI coding agent that proved the concept
- [Charm's Crush](https://github.com/charmbracelet/crush) - Elegant terminal agent

---

## Getting Started

Ready to try Byte? Follow these guides:

- [Installation](getting-started/installation.md) - Set up Byte on your system
- [Getting Started](getting-started/index.md) - Configure and run your first session
- [Configuration](configuration/index.md) - Customize Byte's behavior
- [Commands](commands/index.md) - Learn available commands and workflows
