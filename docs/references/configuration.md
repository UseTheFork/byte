## Documentation

Documentation framework, features, and writing style configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enable_mermaid` | `boolean` | `true` | Use Mermaid for diagrams and charts |
| `framework` | `string` | `mkdocs` | Documentation framework (e.g. mkdocs, vitepress, docusaurus, sphinx) |
| `extra_guidelines` | `array[string]` | - | Additional documentation guidelines |
| `style` | `string` | `diataxis` | Documentation writing style (e.g. diataxis, google, microsoft, minimal) |

## Files

File discovery, watching, and ignore pattern configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ignore` | `array[string]` | `['.byte', '.ruff_cache', '.idea', '.venv', '.env', '.git', '.pytest_cache', '__pycache__', 'node_modules', 'dist']` | List of gitignore-style patterns to exclude from file discovery. Patterns support wildcards and are combined with .gitignore rules. |

## Files > Watch

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enable` | `boolean` | `false` | Enable file watching for AI comment markers (AI:, AI@, AI?, AI!). When enabled, Byte automatically detects changes and processes AI instructions. |

## Gateway

WebSocket JSON-RPC 2.0 gateway server configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enable` | `boolean` | `false` | Whether the gateway server starts at boot |
| `host` | `string` | `127.0.0.1` | Hostname to bind the gateway server to |
| `port` | `integer` | `0` | Port to bind the gateway server to (0 lets the OS choose an available port) |

## Git

Git operations and conventional commit behavior configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enable_scopes` | `boolean` | `false` | Enable scope selection for conventional commits |
| `enable_breaking_changes` | `boolean` | `false` | Enable breaking change detection and confirmation |
| `enable_body` | `boolean` | `true` | Enable commit message body generation |
| `scopes` | `array[string]` | - | Available scopes for conventional commits |
| `description_guidelines` | `array[string]` | - | Additional guidelines for commit descriptions |
| `max_description_length` | `integer` | `72` | Maximum character length for commit descriptions |

## Lint

Code linting and formatting configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enable` | `boolean` | `false` | Enable or disable the linting functionality |
| `commands` | `array[LintCommand]` | `[]` | List of lint commands to run on files with their target extensions |

## Lint > LintCommand

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `command` | `array[string]` | - | Command and arguments to execute for linting (e.g., ['ruff', 'check', '--fix']). Use {file} placeholder to specify where the file path should be inserted, otherwise it will be appended to the end. |
| `languages` | `array[string]` | - | List of language names this command handles (e.g., ['python', 'php']). Empty list means all files. |

## Llm

LLM provider and model assignment configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|

## Llm > Fast

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | `string` | - | The model identifier to use |
| `provider` | `string` | - | The models provider to use |
| `extra_params` | `object` | - | Additional parameters to pass to the model initialization |

## Llm > Standard

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | `string` | - | The model identifier to use |
| `provider` | `string` | - | The models provider to use |
| `extra_params` | `object` | - | Additional parameters to pass to the model initialization |

## Llm > Reasoning

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | `string` | - | The model identifier to use |
| `provider` | `string` | - | The models provider to use |
| `extra_params` | `object` | - | Additional parameters to pass to the model initialization |

## Llm > Coding

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | `string` | - | The model identifier to use |
| `provider` | `string` | - | The models provider to use |
| `extra_params` | `object` | - | Additional parameters to pass to the model initialization |

## Presets

Predefined context and prompt presets

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `string` | - | Unique identifier for the preset, used in /preset <id> command |
| `read_only_files` | `array[string]` | - | Files to add to read-only context |
| `editable_files` | `array[string]` | - | Files to add to editable context |
| `conventions` | `array[string]` | - | Convention files to load |
| `prompt` | `string | null` | - | Preset prompt to load into chat input |
| `load_on_boot` | `boolean` | `false` | Automatically load this preset when byte starts |

## Tui

Terminal UI theme and syntax highlighting configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ui_theme` | `mocha, macchiato, latte, frappe` | `mocha` | Catppuccin theme variant for the CLI interface (mocha/macchiato are dark, latte is light, frappe is cool dark) |
| `syntax_theme` | `github-dark, bw, sas, staroffice, xcode, monokai, lightbulb, rrt` | `monokai` | Pygments theme for code block syntax highlighting in CLI output |

## Web

Web browser automation and scraping configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enable` | `boolean` | `false` | Enable web commands |
| `chrome_binary_location` | `string | null` | - | Path to Chrome/Chromium binary executable for headless browser automation |
