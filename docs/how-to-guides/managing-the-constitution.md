# Manage Your Constitution

**Category**: How-to Guide

This guide walks you through initializing, modifying, and maintaining your project constitution using Byte's built-in commands. You'll learn how to set up your constitution, make changes with natural language requests, and scope rules to specific files.

## Prerequisites

- Byte installed on your system
- A project with a git repository (required for initialization)
- Basic understanding of YAML and markdown

## Step 1: Initialize Your Constitution

The first step is to create your project constitution. Run the initialization command:

```bash
/init
```

The Initialization Workflow walks you through an interactive questionnaire about your project's values and standards:

**Foundational Principles** — You'll be asked whether to enable:
- **DDD** (Domain Driven Design) — Organize business logic into bounded-context domains
- **DRY** (Don't Repeat Yourself) — Eliminate code duplication
- **TDD** (Test Driven Development) — Write tests before implementation
- **YAGNI** (You Aren't Gonna Need It) — Build only for current requirements, not speculation
- **TDA** (Tell, Don't Ask) — Objects expose behavior, not state
- **Strict Typing** — Explicit type annotations on all functions and variables

**Framework & Tooling** — You'll specify which frameworks and linting tools your project uses.

**Additional Input** — You can add custom comments or clarifications.

Answer the prompts honestly. You can change these answers later using the `/constitution` command.

## Step 2: Review What Gets Created

After initialization completes, your constitution is saved at `.byte/constitution/` as a directory of markdown files with YAML frontmatter:

```
.byte/constitution/
├── constitution.md              # Metadata: version, ratified, last_amended
├── principles/
│   ├── ddd.md                   # Domain Driven Design principle
│   ├── dry.md                   # Don't Repeat Yourself principle
│   ├── tdd.md                   # TDD principle
│   └── ... (one per enabled principle)
├── governance/
│   ├── supremacy.md             # Constitution supersedes other practices
│   └── versioning-policy.md     # How to version the constitution
└── sections/
    └── tooling-framework-standards/
        ├── section.md
        └── items/
            ├── framework-standards.md
            └── linting-formatting.md
```

Each file is human-readable, version-controlled, and easy to edit. You can peek inside any `.md` file to see the content and structure.

## Step 3: Modify Your Constitution

After initialization, use the `/constitution` command to request changes in plain language:

```bash
/constitution Add a new principle about error handling
```

```bash
/constitution Remove the TDD principle
```

```bash
/constitution Update the versioning policy to use calendar versioning
```

The Constitution Agent reads your request, presents the current constitution, and makes surgical edits — only the changes you asked for are modified. Nothing else is touched.

### Common Modification Tasks

**Add a principle:**

```bash
/constitution Add a principle: "Configuration as Code — All configuration must be version-controlled and environment-specific."
```

**Add a section with items:**

```bash
/constitution Add a new section called "Security Requirements" with these items: (1) Secret Management, (2) API Authentication
```

**Delete a section:**

```bash
/constitution Remove the "Security Requirements" section
```

**Update a governance rule:**

```bash
/constitution Change the Supremacy rule to reflect that the constitution can be overridden by explicit board decision
```

## Step 4: Scope Sections to File Patterns

Sections can be scoped to specific directories or file patterns using glob patterns. This lets you enforce different rules for different parts of your codebase.

**Request a scoped section:**

```bash
/constitution Add a section called "Authentication Standards" that applies only to src/byte/auth/** and src/byte/api/**
```

When you make this request, the Constitution Agent adds the `applies_to` field to the section:

```yaml
---
id: authentication-standards
name: Authentication Standards
applies_to:
  - "src/byte/auth/**"
  - "src/byte/api/**"
order: 1
---
```

When agents work on files matching these patterns, they see the authentication standards. When they work on unrelated files, they don't. This keeps the constitution focused and relevant.

**Update the scope:**

```bash
/constitution Change the applies_to patterns for "Authentication Standards" to include src/byte/oauth/** as well
```

## Step 5: Understand Semantic Versioning

Your constitution version follows semantic versioning. Each time you request a change, the Constitution Agent proposes a version bump:

- **MAJOR** — Backward-incompatible changes: removing a principle, redefining governance rules, or fundamentally altering existing guidance
- **MINOR** — Adding new principles, adding new sections, or materially expanding existing guidance
- **PATCH** — Wording clarifications, typo fixes, reorganization, or other non-semantic refinements

Example: If your constitution is at version `0.2.0` and you add a new principle, the agent proposes bumping to `0.3.0` (MINOR).

You can accept the proposed version or override it:

```bash
/constitution Add a principle about documentation. Bump the version to 1.0.0 instead.
```

The version is stored in `.byte/constitution/constitution.md` and is always visible when you review the constitution.

## Step 6: Verify Your Constitution

At any time, you can view the rendered constitution by checking `.byte/constitution/constitution.md` or by running a query:

```bash
/constitution Show me the current constitution
```

This displays the full text with all principles, sections, and governance rules.

## Example: Build a Constitution from Scratch

Here's a realistic sequence:

**Initialize with defaults:**

```bash
/init
# Answer: Yes to DDD, DRY, TDD, YAGNI, TDA, Strict Typing
# Framework: FastAPI
# Linting: Ruff
```

**Add a custom principle:**

```bash
/constitution Add a principle: "Error Handling — All errors must be logged with context and never silently swallowed."
```

**Add a security section for auth code:**

```bash
/constitution Add a section called "Security Standards" with items: (1) Secret Management — No hardcoded secrets, (2) Authentication — Use standard libraries, never roll your own. Apply this section only to src/byte/auth/**
```

**Refine the DRY principle:**

```bash
/constitution Update the DRY principle to emphasize that shared logic must live in src/byte/support/
```

Your constitution now reflects your project's actual values and enforces them on every AI-assisted change.

## Next Steps

Now that you've created and modified your constitution, review the Explanation section to understand the deeper concepts: how the constitution is loaded, how it reaches agents, and how to think about governance.

Check the `/constitution` command output for any feedback or clarifications the agent provides during each change.

