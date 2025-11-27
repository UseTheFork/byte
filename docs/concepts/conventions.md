# Conventions

Conventions are Markdown files stored in `.byte/conventions/` that describe how code should be written in your project. The AI automatically receives these conventions before generating any code, ensuring consistency across all suggestions and modifications.

![File context showing read-only and editable files](../images/recording/command_convention.gif)

---

## Creating Conventions

### Using the Convention Command

Byte can automatically generate convention documents by analyzing your codebase:

```
> /convention
```

The command will:

1. Prompt you to select a convention type (style guide, architecture, etc.)
2. Analyze your codebase to extract relevant patterns
3. Generate a focused convention document
4. Save it to `.byte/conventions/`
5. Load it into the current session

Available convention types include:

- **Language Style Guide** - Naming, formatting, type hints, imports
- **Project Architecture** - Directory structure, module organization, design patterns
- **Comment Standards** - Docstring format, inline comments, documentation practices
- **Code Patterns** - Design patterns, error handling, async/await usage
- **Project Tooling** - Build systems, package managers, dev tools
- **Documentation** - Documentation structure, writing style, examples
- **Frontend Code Patterns** - Component structure, state management, UI patterns
- **Backend Code Patterns** - API design, database access, service layer organization
- **Other** - Custom convention with your own focus

### Manual Convention Files

You can also manually create convention documents as Markdown files in `.byte/conventions/`:

### File Format

Conventions use standard Markdown formatting:

```markdown
# Python Style Guide

## General Rules

- Use snake_case for functions and variables
- Use PascalCase for class names
- Maximum line length: 88 characters

## Documentation

All public functions require docstrings with usage examples.
```

---

## How Conventions Work

### Automatic Loading

When Byte starts or when you generate a new convention, it:

1. Scans `.byte/conventions/` for all `.md` files
2. Loads each file's content
3. Formats them with metadata (filename and source path)
4. Stores them in memory for quick access

Newly generated conventions are immediately available in the current session without restarting Byte.

---

## Best Practices

### Be Specific

Provide concrete examples rather than abstract rules:

**Less effective:**

```markdown
Use good naming conventions.
```

**More effective:**

```markdown
Use descriptive names:

- `user_repository` not `ur`
- `calculate_total_price()` not `calc()`
```

### Show Code Examples

Include actual code snippets demonstrating the pattern:

```markdown
## Error Handling

Catch specific exceptions:

\`\`\`python
try:
result = await process_file(path)
except FileNotFoundError:
logger.error(f"File not found: {path}")
return None
\`\`\`
```

### Keep It Current

Update conventions as your project evolves. Remove outdated rules and add new patterns as you discover them.

### Organize by Topic

Create separate files for different aspects:

- `PYTHON_STYLE.MD` - Language-specific formatting
- `ARCHITECTURE.MD` - System design patterns
- `API_DESIGN.MD` - API conventions
- `TESTING.MD` - Test organization and patterns
