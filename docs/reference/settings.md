# Byte Configuration Settings

Byte's configuration system uses a YAML file located at `.byte/config.yaml` to control all aspects of the application's behavior. Configuration is organized into logical sections covering CLI behavior, LLM providers, file handling, and feature-specific settings.

---

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

| Field    | Type            | Default                                                                                                                    | Description                                                                                                                         |
| -------- | --------------- | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `ignore` | `array[string]` | `['.byte/cache', '.ruff_cache', '.idea', '.venv', '.env', '.git', '.pytest_cache', '__pycache__', 'node_modules', 'dist']` | List of gitignore-style patterns to exclude from file discovery. Patterns support wildcards and are combined with .gitignore rules. |

## Files > Watch

| Field    | Type      | Default | Description                                                                                                                                       |
| -------- | --------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `enable` | `boolean` | `false` | Enable file watching for AI comment markers (AI:, AI@, AI?, AI!). When enabled, Byte automatically detects changes and processes AI instructions. |

## Edit_Format

| Field                   | Type      | Default | Description                                                                                                                                               |
| ----------------------- | --------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `enable_shell_commands` | `boolean` | `false` | Enable execution of shell commands from AI responses. When disabled, shell command blocks will not be executed.                                           |
| `mask_message_count`    | `integer` | `1`     | Number of recent AI messages to exclude from masking. Messages older than this count will have their SEARCH/REPLACE blocks removed to reduce token usage. |

## Web

| Field                    | Type      | Default                  | Description                                                               |
| ------------------------ | --------- | ------------------------ | ------------------------------------------------------------------------- |
| `enable`                 | `boolean` | `false`                  | Enable web commands                                                       |
| `chrome_binary_location` | `string`  | `/usr/bin/google-chrome` | Path to Chrome/Chromium binary executable for headless browser automation |
