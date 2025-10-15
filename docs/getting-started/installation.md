# Installation

Install Byte to start building with AI-powered coding assistance. Byte is a human-in-the-loop coding agent that runs as a command-line tool.

---

## Installing Byte

### Using uv (Recommended)

The fastest way to install Byte is with **uv**, a modern Python package installer:

```bash
$ curl -LsSf https://astral.sh/uv/install.sh | sh
$ uv tool install byte
```

### Using pip

Install Byte using pip if you prefer traditional Python tooling:

```bash
$ pip install byte
```

### Using Nix Flakes

For NixOS users or those with Nix flakes enabled, add Byte to your configuration:

```nix
{
  inputs = {
    byte.url = "github:UseTheFork/byte";
  };
}
```

Include it in your system packages:

```nix
environment.systemPackages = [
  inputs.byte.packages.${system}.default
];
```

Or run directly without installation:

```bash
$ nix run github:UseTheFork/byte
```

---

## Verify Installation

Confirm Byte installed successfully:

```bash
$ byte --version
```

You should see the version number.

---

## Next Steps

Now that Byte is installed, learn how to use it:

- [Getting Started](index.md) - Configure and run your first session
- [Configuration](../configuration/index.md) - Customize Byte's behavior
- [Commands](../commands/index.md) - Explore available commands
