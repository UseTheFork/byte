# Installation Guide

**Category**: Tutorial

This guide walks you through installing Byte on your system. Choose the installation method that works best for you.

## Requirements

Byte requires **Python 3.14 or later**. Check your Python version before proceeding:

```bash
python --version
```

If you don't have Python 3.14 installed, download it from [python.org](https://www.python.org/downloads/) or use your system's package manager.

## Installation Methods

### Option 1: pip (Universal)

The simplest way to install Byte on any system with Python 3.14+ installed:

```bash
pip install byte-ai-cli
```

This method works on macOS, Linux, and Windows. It installs Byte and all its dependencies into your Python environment.

### Option 2: uv (Recommended)

[uv](https://docs.astral.sh/uv/) is Byte's preferred installation tool. It's faster, more reliable, and handles Python versions automatically:

```bash
uv tool install byte-ai-cli
```

This approach is especially useful if you work with multiple Python projects. uv isolates Byte in its own environment and automatically manages its dependencies.

If you don't have uv installed, follow the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) first.

### Option 3: NixOS (Flake)

If you use NixOS or Nix, you can install Byte from the project's Nix flake:

```bash
nix flake show github:usethefork/byte
```

To add Byte to your `flake.nix` project:

```nix
{
  inputs = {
    byte.url = "github:usethefork/byte";
  };

  outputs = { byte, ... }: {
    devShells.default = pkgs.mkShell {
      buildInputs = [ byte.packages.default ];
    };
  };
}
```

Then enter the development shell:

```bash
nix flake update
nix develop
```

---

Byte is now ready to use. See the next tutorial for configuration and first steps.
