# MkDocs Documentation Style Guide

## Structure

- Use clear, descriptive headers with title case
- Start with a brief overview paragraph
- Use horizontal rules (`---`) to separate major sections
- Keep navigation hierarchy shallow (max 3 levels)

## Content

- Lead with practical examples before theory
- Use second person ("you") for instructions
- Keep paragraphs short (2-4 sentences)
- Use active voice: "uv installs packages" not "packages are installed"

## Code Examples

- Show minimal, runnable examples
- Include shell prompts (`$` for Unix, `PS>` for PowerShell)
- Use syntax highlighting with language identifiers
- Provide context before code blocks

Example:

```bash
$ uv run byte --help
```

## Formatting

- Bold for UI elements and important terms on first use
- Inline code for commands, file names, and variable names
- Use admonitions sparingly (Tip, Note, Warning)
- Keep line length reasonable (80-100 chars for readability)

## Admonitions

Use sparingly and appropriately:

```markdown
!!! note
Additional context that enhances understanding.

!!! warning
Critical information about potential issues.

!!! tip
Helpful shortcuts or best practices.
```

## Links

- Use descriptive link text, not "click here"
- Link to concepts on first mention
- Use relative paths for internal links
- Keep URLs readable when possible

## Lists

- Use bullet points for unordered items
- Use numbered lists only for sequential steps
- Keep list items parallel in structure
- Nest lists sparingly (max 2 levels)

## Tables

- Use for comparing options or showing structured data
- Keep columns narrow and scannable
- Include headers for all columns
- Avoid complex nested content

## Best Practices

- Start documentation with "Getting Started" or "Quick Start"
- Provide working examples before detailed API docs
- Include real-world use cases
- Update examples when code changes
- Test all code examples before publishing
