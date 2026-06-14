# Configure LLM Providers and Models

**Category**: How-to Guide

This guide shows you how to set up and configure LLM providers in Byte. You'll learn how to choose between Anthropic, Gemini, and OpenAI, set up API keys, and customize model assignments for different task types.

## Prerequisites

- Byte installed on your system
- An API key for at least one LLM provider (Anthropic, Gemini, or OpenAI)

## Step 1: Obtain an API Key

Byte requires at least one API key for an LLM provider. Choose the provider that works best for you:

**Anthropic**: Visit [console.anthropic.com](https://console.anthropic.com) to create an account and generate an API key.

**Gemini**: Go to [Google AI Studio](https://aistudio.google.com/apikey) to create an API key for Gemini models.

**OpenAI**: Sign up at [platform.openai.com](https://platform.openai.com) and create an API key from the account settings.

## Step 2: Set the API Key as an Environment Variable

Byte reads API keys from environment variables. Add your key to a `.env` file in your project root:

```bash
# .env (in your project root)
ANTHROPIC_API_KEY=your-api-key-here
```

Byte loads this file on startup. Replace `ANTHROPIC_API_KEY` with `GEMINI_API_KEY` or `OPENAI_API_KEY` if using a different provider.

If you prefer not to use a `.env` file, set the environment variable directly in your shell:

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

You must set at least one of these variables before running Byte. If none are configured, Byte will exit with an error.

## Step 3: Configure Your Default Provider (First Run)

When you run Byte for the first time, it prompts you to select a default LLM provider:

```
Please choose a default provider:

1. anthropic
2. gemini
3. openai

Select LLM Provider:
```

Your choice populates `.byte/config.jsonc` with model assignments for that provider. You can skip this step if you want to configure manually.

## Step 4: Customize Model Assignments

Byte allocates models across four slots, each optimized for different tasks. Edit `.byte/config.jsonc` in your project root:

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/UseTheFork/byte/refs/heads/main/schema.json",
  "llm": {
    "fast": {
      "model": "claude-haiku-4-5",
      "provider": "anthropic"
    },
    "standard": {
      "model": "claude-sonnet-4-6",
      "provider": "anthropic"
    },
    "reasoning": {
      "model": "claude-opus-4-6",
      "provider": "anthropic"
    },
    "coding": {
      "model": "claude-haiku-4-5",
      "provider": "anthropic"
    }
  }
}
```

Each slot has a `model` and `provider` field. The available models and their specifications are managed by Byte and depend on your provider.

### Model Slot Purposes

- **fast**: Quick, lightweight tasks (low latency, lower cost)
- **standard**: General-purpose tasks (balanced speed and quality)
- **reasoning**: Complex problem-solving and analysis (highest quality)
- **coding**: Code generation and refactoring tasks

## Example 1: Anthropic-Only Setup

All models from Anthropic:

```jsonc
{
  "llm": {
    "fast": {
      "model": "claude-haiku-4-5",
      "provider": "anthropic"
    },
    "standard": {
      "model": "claude-sonnet-4-6",
      "provider": "anthropic"
    },
    "reasoning": {
      "model": "claude-opus-4-6",
      "provider": "anthropic"
    },
    "coding": {
      "model": "claude-haiku-4-5",
      "provider": "anthropic"
    }
  }
}
```

Make sure `ANTHROPIC_API_KEY` is set in your `.env` file.

## Example 2: Gemini-Only Setup

All models from Google Gemini:

```jsonc
{
  "llm": {
    "fast": {
      "model": "gemini-3.5-flash",
      "provider": "gemini"
    },
    "standard": {
      "model": "gemini-3.5-flash",
      "provider": "gemini"
    },
    "reasoning": {
      "model": "gemini-3.1-pro-preview",
      "provider": "gemini"
    },
    "coding": {
      "model": "gemini-3.5-flash",
      "provider": "gemini"
    }
  }
}
```

Make sure `GEMINI_API_KEY` is set in your `.env` file.

## Example 3: OpenAI-Only Setup

All models from OpenAI:

```jsonc
{
  "llm": {
    "fast": {
      "model": "gpt-5.4-mini",
      "provider": "openai"
    },
    "standard": {
      "model": "gpt-5.4",
      "provider": "openai"
    },
    "reasoning": {
      "model": "gpt-5.5",
      "provider": "openai"
    },
    "coding": {
      "model": "gpt-5.4",
      "provider": "openai"
    }
  }
}
```

Make sure `OPENAI_API_KEY` is set in your `.env` file.

## Example 4: Mixed-Provider Setup

Combine providers to optimize cost and performance:

```jsonc
{
  "llm": {
    "fast": {
      "model": "gemini-3.5-flash",
      "provider": "gemini"
    },
    "standard": {
      "model": "claude-sonnet-4-6",
      "provider": "anthropic"
    },
    "reasoning": {
      "model": "gpt-5.5",
      "provider": "openai"
    },
    "coding": {
      "model": "claude-haiku-4-5",
      "provider": "anthropic"
    }
  }
}
```

In this example:
- Gemini handles fast tasks (lowest cost)
- Anthropic handles standard and coding tasks (balanced performance)
- OpenAI handles reasoning tasks (highest capability)

Remember to set all three API keys in your `.env` file when mixing providers:

```bash
# .env
ANTHROPIC_API_KEY=your-anthropic-key
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
```

## Troubleshooting

**Error: "Missing required API key"**

You haven't set any API key environment variables. Add at least one of `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, or `OPENAI_API_KEY` to your `.env` file and restart Byte.

**Error: "Unknown configuration"**

A model name or provider in your config doesn't match available options. Check that the `model` value is valid for your `provider`.

**Models aren't changing on next run**

Byte caches model configuration. After editing `.byte/config.jsonc`, restart Byte to pick up your changes.

## Next Steps

Now that you've configured your providers and models, explore how to use Byte with your chosen configuration. Check the tutorials for hands-on examples.
