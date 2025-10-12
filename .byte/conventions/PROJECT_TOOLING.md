# Project Tooling

## Build System

- **uv**: Modern Python package installer and resolver
- **pyproject.toml**: Project configuration, dependencies, and tool settings
- Build backend: `uv_build` (>= 0.8.10, < 0.9.0)
- Python: >= 3.12 required

## Key Dependencies

- **LangChain/LangGraph**: AI agent framework with graph-based workflows
- **Pydantic**: Data validation and settings management (v2.11+)
- **Rich**: Terminal UI rendering and formatting
- **Click**: CLI framework (entry point: `byte.core.cli:cli`)
- **prompt-toolkit**: Interactive command-line interface
- **GitPython**: Git repository operations
- **watchfiles**: File system monitoring
- **ripgrepy**: Fast file searching
- **aiosqlite**: Async database for checkpointing

## Running

- Entry point: `uv run byte` or install and use `byte` command
- Scripts defined in pyproject.toml: `scripts.byte = "byte.core.cli:cli"`
