# Configuration

**Category**: Explanation

Byte's configuration is straightforward and declarative. You define your preferences in a single JSONC file at `.byte/config.jsonc`, and Byte loads it at startup. Configuration is organized into sections—documentation framework, LLM models, linting, files, web, git, gateway, terminal UI, and presets. Invalid config produces clear error messages; changes take effect on the next invocation.

## The Config File

Configuration lives at `.byte/config.jsonc` in your project root. It's JSON with comments—use `//` for single-line notes, `/* */` for blocks. This is where you tell Byte how to behave.

When you run any Byte command, the config is loaded and validated. If something is wrong—a typo, an invalid value, a missing required field—Byte reports the error clearly and exits. Fix the problem and run again. Changes take effect immediately on the next invocation; no restart needed.

## Configuration Sections

Configuration is organized into these sections:

**documentation** — Your documentation framework (mkdocs, vitepress, docusaurus, sphinx), whether Mermaid diagrams are enabled, and any additional writing guidelines.

**files** — File discovery patterns, which AI comment markers to watch for (AI:, AI@, AI?, AI!), and gitignore-style patterns for files Byte should ignore.

**gateway** — WebSocket JSON-RPC 2.0 gateway server: whether to enable it, what host to bind to, and which port to use.

**git** — Conventional commit behavior: commit scope selection, breaking change detection, and message guidelines.

**lint** — Linting and formatting commands: which commands to run and which file types they handle.

**llm** — LLM model assignment for four task types: fast (quick tasks), standard (general-purpose), reasoning (complex analysis), and coding (code generation).

**presets** — Predefined context and prompt presets: files to load automatically, conventions to apply, and features to enable.

**tui** — Terminal UI: color theme (Catppuccin variants) and code syntax highlighting preference.

**web** — Web browser automation: Chrome/Chromium binary location and feature toggles.

## Example Configuration

Here's a minimal configuration that works out of the box:

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/UseTheFork/byte/refs/heads/main/schema.json",
  "documentation": {
    "framework": "mkdocs",
  },
  "llm": {
    "fast": {
      "model": "claude-haiku-4-5",
      "provider": "anthropic",
    },
    "standard": {
      "model": "claude-sonnet-4-6",
      "provider": "anthropic",
    },
    "reasoning": {
      "model": "claude-opus-4-6",
      "provider": "anthropic",
    },
    "coding": {
      "model": "claude-haiku-4-5",
      "provider": "anthropic",
    },
  },
}
```

The `$schema` field enables validation and autocomplete in most editors.

## Finding Configuration Options

The full configuration reference is rendered inline below. Every available setting, its type, default value, and what it controls is documented here — no need to go elsewhere.

{% include "references/configuration.md" %}

The reference above is organized by section. Find what you need by domain, then drop it into your `.byte/config.jsonc`.

## Key Takeaways

1. **Configuration is declarative** — Define it in `.byte/config.jsonc`, and Byte respects it
2. **It's organized by section** — Find what you need by domain (llm, git, lint, etc.)
3. **It's validated at load time** — Invalid config produces clear error messages
4. **Changes take effect on next invocation** — No restart required
5. **Full reference is available** — See the settings reference for every option
