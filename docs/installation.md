# Installation

Byte is a CLI-powered, human-in-the-loop flow coding agent built with Python 3.12+.

## Prerequisites

- Python 3.12 or higher
- Git (for cloning the repository)

## Quick Install

### Using uv (Recommended)

The fastest way to install Byte is using [uv](https://github.com/astral-sh/uv), a modern Python package installer:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Byte
uv tool install byte
```

### Using pip

```bash
pip install byte
```

### Using Nix Flakes

For NixOS users or those using Nix package manager with flakes enabled:

```nix
# Add to your flake.nix inputs
{
  inputs = {
    byte.url = "github:UseTheFork/byte";
    # ... other inputs
  };
}
```

Then include it as a package in your system or home-manager configuration:

```nix
# In your system configuration
environment.systemPackages = [
  inputs.byte.packages.${system}.default
];

# Or in home-manager
home.packages = [
  inputs.byte.packages.${system}.default
];
```

Alternatively, run Byte directly without installation:

```bash
nix run github:UseTheFork/byte
```

## Development Installation

To contribute to Byte or run it from source:

```bash
# Clone the repository
git clone https://github.com/yourusername/byte.git
cd byte

# Install with uv (includes dev dependencies)
uv sync

# Run Byte
uv run byte
```

### Optional: Nix Development Environment

For a fully reproducible development environment using Nix flakes:

```bash
# Requires Nix with flakes enabled
nix develop

# Or use direnv for automatic activation
echo "use flake" > .envrc
direnv allow
```

## Verify Installation

Confirm Byte is installed correctly:

```bash
byte --version
byte --help
```

## Next Steps

- Read the [Quick Start Guide](quickstart.md) to begin using Byte
- Explore [Configuration](configuration.md) options
- Learn about [Commands](commands.md) and workflows
