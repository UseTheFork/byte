# Byte Configuration Settings

This document describes all available configuration options for Byte.

## Cli

| Field          | Type                                                               | Default   | Description                                                                                                    |
| -------------- | ------------------------------------------------------------------ | --------- | -------------------------------------------------------------------------------------------------------------- |
| `ui_theme`     | `mocha, macchiato, latte, frappe`                                  | `mocha`   | Catppuccin theme variant for the CLI interface (mocha/macchiato are dark, latte is light, frappe is cool dark) |
| `syntax_theme` | `github-dark, bw, sas, staroffice, xcode, monokai, lightbulb, rrt` | `monokai` | Pygments theme for code block syntax highlighting in CLI output                                                |

## Llm

| Field   | Type                        | Default     | Description                               |
| ------- | --------------------------- | ----------- | ----------------------------------------- |
| `model` | `anthropic, gemini, openai` | `anthropic` | The LLM provider to use for AI operations |

## Llm > Gemini

| Field          | Type      | Default | Description                                                |
| -------------- | --------- | ------- | ---------------------------------------------------------- |
| `enabled`      | `boolean` | `false` | Whether this LLM provider is enabled and available for use |
| `api_key`      | `string`  | -       | API key for authenticating with the LLM provider           |
| `model_params` | `object`  | -       | Additional parameters to pass to the model initialization  |

## Llm > Anthropic

| Field          | Type      | Default | Description                                                |
| -------------- | --------- | ------- | ---------------------------------------------------------- |
| `enabled`      | `boolean` | `false` | Whether this LLM provider is enabled and available for use |
| `api_key`      | `string`  | -       | API key for authenticating with the LLM provider           |
| `model_params` | `object`  | -       | Additional parameters to pass to the model initialization  |

## Llm > Openai

| Field          | Type      | Default | Description                                                |
| -------------- | --------- | ------- | ---------------------------------------------------------- |
| `enabled`      | `boolean` | `false` | Whether this LLM provider is enabled and available for use |
| `api_key`      | `string`  | -       | API key for authenticating with the LLM provider           |
| `model_params` | `object`  | -       | Additional parameters to pass to the model initialization  |

## Lint

| Field      | Type                 | Default | Description                                                        |
| ---------- | -------------------- | ------- | ------------------------------------------------------------------ |
| `enable`   | `boolean`            | `true`  | Enable or disable the linting functionality                        |
| `commands` | `array[LintCommand]` | `[]`    | List of lint commands to run on files with their target extensions |

## Lint > LintCommand

| Field        | Type            | Default | Description                                                                                         |
| ------------ | --------------- | ------- | --------------------------------------------------------------------------------------------------- |
| `command`    | `string`        | -       | Shell command to execute for linting (e.g., 'ruff check --fix')                                     |
| `extensions` | `array[string]` | -       | List of file extensions to run this command on (e.g., ['.py', '.pyi']). Empty list means all files. |

## Files

| Field    | Type            | Default | Description                                                                                                                         |
| -------- | --------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `ignore` | `array[string]` | `[]`    | List of gitignore-style patterns to exclude from file discovery. Patterns support wildcards and are combined with .gitignore rules. |

## Files > Watch

| Field    | Type      | Default | Description |
| -------- | --------- | ------- | ----------- |
| `enable` | `boolean` | `true`  |             |

## Edit_Format

| Field                   | Type      | Default | Description                                                                                                     |
| ----------------------- | --------- | ------- | --------------------------------------------------------------------------------------------------------------- |
| `enable_shell_commands` | `boolean` | `true`  | Enable execution of shell commands from AI responses. When disabled, shell command blocks will not be executed. |

## Web

| Field                    | Type     | Default                  | Description                                                               |
| ------------------------ | -------- | ------------------------ | ------------------------------------------------------------------------- |
| `chrome_binary_location` | `string` | `/usr/bin/google-chrome` | Path to Chrome/Chromium binary executable for headless browser automation |
