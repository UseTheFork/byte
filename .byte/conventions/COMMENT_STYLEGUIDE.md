# Comment Styling Guide

This guide outlines the best practices for writing comments in this repository. The goal is to maintain clarity and consistency across all code, regardless of the programming language.

## General Principles

1. **Explain the "Why", Not the "What"**: Code should be self-documenting. Use comments to explain complex logic, design decisions, or the intent behind a piece of code that might not be immediately obvious.

1. **Keep it Concise**: Write short, clear sentences. Avoid long narratives.

1. **Placement**:

   - Place comments on the line immediately preceding the code block they describe.
   - Inline comments can be used to clarify individual lines, arguments, or variable declarations.

## Formatting

- Start comments with the comment character followed by a single space (e.g., `# `, `// `).
- Use complete sentences with proper capitalization and punctuation.
- For multi-line comments, each line should begin with the comment character.

## Function Documentation

For functions, methods, or reusable components, provide a summary that includes:

1. A brief description of its purpose.
1. An example of usage, including input and expected output.
1. (Optional) Type signatures if the language is dynamically typed.

### Example (Nix)

```nix
# a basic function to fetch a specified user's public keys from github .keys url
# `fetchKeys "username` -> "ssh-rsa AAAA...== username@hostname"
#@ String -> String
fetchKeys = username: (builtins.fetchurl "https://github.com/${username}.keys");
```

## Special Tags

Use standard tags to highlight specific information:

- `TODO:` for planned features or improvements.
- `FIXME:` for known issues that need to be addressed.
