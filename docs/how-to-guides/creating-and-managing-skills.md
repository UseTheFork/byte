# Create and Manage Skills

**Category**: How-to Guide

This guide shows you how to create, edit, and manage skills in Byte. You'll learn what skills are, how they're organized, how to write them effectively, and how to leverage the skill creation workflow.

## Prerequisites

- Byte installed on your system
- Basic understanding of YAML (for frontmatter)
- Familiarity with markdown formatting

## Step 1: Understand What Skills Are

A skill is a reusable instruction package that guides agents on how to perform specific tasks. Every skill is a `SKILL.md` file containing:

- **YAML frontmatter** — Metadata including `name` (required), `description` (required), and optional `version`
- **Markdown body** — The actual instructions that agents use when the skill is loaded

When an agent needs to perform work, Byte loads relevant skills and injects their instructions into the agent's prompt. This gives agents domain-specific knowledge and task-specific guidance without hardcoding behavior into the application.

Skills are discovered and loaded automatically, with the system scanning three directories on startup (see Step 3 for priority details).

## Step 2: Understand Skill Directory Structure

Skills live in a simple hierarchy. Each skill occupies a directory with a required `SKILL.md` file and optional supporting references:

```
skill-name/
├── SKILL.md                 (required)
└── references/              (optional)
    ├── reference-one.md
    ├── reference-two.md
    └── guide.md
```

- **SKILL.md** — The core skill file with frontmatter and instructions
- **references/** — Optional directory containing supplementary `.md` files

The references directory is automatically discovered.

> **Security Boundary: Byte Does Not Execute External Files**
>
> Byte reads **only** `SKILL.md` and markdown files in `references/`. Shell scripts, Python files, compiled binaries, or any other executable files in a skill directory are completely ignored — never loaded, parsed, or executed. This is by design. Skills are pure instruction packages; they have no capability to run code or access the filesystem. If you need dynamic behavior, encode it in the skill instructions themselves and let agents decide how to implement it.

## Step 3: Learn the Three-Tier Skill Priority System

Byte discovers skills from three sources, scanned in ascending priority order. When two skills share the same name, the higher-priority source wins:

1. **Builtin skills** (lowest priority) — Shipped with Byte in the `skills/builtin` directory
2. **Agent-level skills** — User skills in `.agent/skills/` (git root)
3. **Project-level skills** (highest priority) — User skills in `.byte/skills/`

This three-tier system enables you to override builtin skills on a per-project basis. For example, you could create a project-level skill with the same name as a builtin skill, and your version would be used instead.

When you create or edit a skill, the skill registry is automatically reloaded. The priority order ensures that custom (project-level) skills always take precedence.

## Step 4: Create a Skill Manually

You can write a skill by hand and save it to the appropriate directory.

**Step 4.1: Create the skill directory**

```bash
mkdir -p .byte/skills/my-skill-name
```

**Step 4.2: Write the SKILL.md file**

Create `.byte/skills/my-skill-name/SKILL.md` with the following structure:

```yaml
---
name: my-skill-name
description: A short, clear description of what this skill does and when to use it.
version: 1.0.0
---

# Skill Body

Write your skill instructions in markdown here. This is the content that agents will see when the skill is loaded.

## Section Example

You can organize instructions with headings and subsections.

### Best Practices

- Write clear, imperative instructions
- Use examples if helpful
- Keep the main body under ~500 lines; use references/ for larger docs
```

The YAML frontmatter requires:

- `name` — A unique identifier for the skill
- `description` — A short explanation of what the skill does (this is the primary trigger mechanism; see Step 6)
- `version` — Optional version string

The markdown body is everything after the frontmatter `---` closing marker.

**Step 4.3: Verify the skill is loaded**

Byte automatically discovers and loads the skill on startup. If you created the skill while Byte was running, the skill loader reloads automatically when you invoke a command.

## Step 5: Create a Skill Using the `/skill` Command

The `/skill` command provides an interactive workflow for building skills with agent assistance. Instead of writing SKILL.md manually, you describe what you want and the agent helps you create it.

**Step 5.1: Invoke the command**

```bash
/skill I want to create a skill that helps format commit messages
```

**Step 5.2: Understand the workflow phases**

The `/skill` command runs through three main phases:

1. **create-instruction** — The system analyzes your request and conversation history to synthesize a clear instruction for the Skill Creator Agent
2. **capture-intent** — The Skill Creator Agent interviews you about your skill:
   - What should the skill enable?
   - When should it trigger? (what phrases or contexts?)
   - What's the expected output format?
   - Do you want test cases?
3. **create-skill** — The agent creates the skill, then presents it for review

If you're satisfied with the skill, you approve it and the workflow completes. If you have feedback, the agent iterates based on your input.

**Step 5.3: What the agent creates**

The agent writes a complete `SKILL.md` file in `.byte/skills/` with proper frontmatter, clear instructions, and any reference files you discussed. The skill is immediately available after creation.

## Step 6: Write Effective Descriptions

The skill `description` in the YAML frontmatter is your primary trigger mechanism. Byte reads descriptions to decide which skills are relevant for a given task. A weak description means the skill won't load when needed.

**Bad description** (too generic, undertriggers):

```yaml
description: A skill for writing
```

**Good description** (specific, lists trigger phrases):

```yaml
description: Format and improve commit messages following conventional commits style. Use this skill whenever the user mentions commits, commit messages, git history, changelog, semantic versioning, or wants to improve the clarity of their code history.
```

The good description includes:

- What the skill does (format and improve commit messages)
- The specific methodology (conventional commits)
- Trigger contexts and phrases (commits, commit messages, git history, changelog, etc.)

Be "pushy" with your descriptions. Claude has a tendency to undertrigger skills if the description is passive or vague. Explicitly list contexts where the skill applies, even if they seem obvious.

## Step 7: Add and Manage Reference Files

Reference files are supplementary markdown documents stored in the `references/` directory within your skill folder. They're automatically discovered and can be loaded on demand.

**Step 7.1: Create references manually**

Create a `references/` directory inside your skill folder and add `.md` files:

```bash
mkdir -p .byte/skills/my-skill-name/references
echo "# Reference Content" > .byte/skills/my-skill-name/references/guide.md
```

Files are discovered automatically. Use references to keep your main `SKILL.md` focused and under ~500 lines.

## Step 8: Edit Existing Skills

Open `.byte/skills/your-skill-name/SKILL.md`, make changes, and save. The next time a skill is loaded (or on the next command invocation), the registry reloads and picks up your changes.

## Step 9: Understand Skill Loading and Priority

Understanding how skills are discovered and loaded helps you manage skill priority and override behavior.

**How skill loading works:**

1. On startup (or reload), the system scans all three skill directories in order
2. For each directory, it finds all `SKILL.md` files recursively
3. Each skill is parsed and stored in memory by skill ID (normalized name)
4. When two skills share the same ID, the higher-priority source overwrites the lower-priority one
5. The final merged set of skills is available to agents

**Priority in action:**

If you have:

- Builtin skill: `my-skill`
- Agent-level skill: `my-skill`
- Project-level skill: `my-skill`

The project-level version is used. This allows you to customize builtin behavior per-project.

**Reloading skills:**

When you create or edit a skill, the skill registry automatically reloads. Manual file edits are picked up on the next reload cycle.

## Example 1: Simple Manual Skill

Here's a minimal skill created by hand:

```bash
mkdir -p .byte/skills/greeting
```

`.byte/skills/greeting/SKILL.md`:

```yaml
---
name: greeting
description: Generate friendly, contextual greetings. Use this skill whenever the user wants a greeting, introduction, or welcome message.
---

# Greeting Skill

Generate friendly greetings tailored to the context provided by the user.

## Guidelines

- Match the tone to the context (formal, casual, enthusiastic)
- Include a personal touch if information is available
- Keep greetings concise but warm
```

This skill is now available and will be loaded when agents determine it's relevant.

## Example 2: Skill With References

Here's a skill that uses references for extended documentation:

`.byte/skills/api-documentation/SKILL.md`:

```yaml
---
name: api-documentation
description: Generate clear, well-structured API documentation with examples. Use this skill when the user wants to document APIs, REST endpoints, functions, classes, or any code interface.
version: 1.0.0
---

# API Documentation Skill

Generate comprehensive API documentation that's clear, accurate, and easy to navigate.

## Core Principles

- Prioritize clarity over brevity
- Always include examples
- Document parameters, return types, and exceptions
- Use consistent formatting

For detailed guidelines on specific documentation formats, see the references in this skill:

- `openapi-guide.md` — Detailed OpenAPI 3.0 documentation standards
- `examples.md` — Real-world documentation examples
```

Then create the references:

```bash
mkdir -p .byte/skills/api-documentation/references
```

`.byte/skills/api-documentation/references/openapi-guide.md` and `.byte/skills/api-documentation/references/examples.md` contain supplementary content. This keeps `SKILL.md` lean while providing rich supporting material on demand.

## Next Steps

Now that you can create and manage skills, explore how to use them effectively in your workflows. Check the tutorials for hands-on examples of common skill patterns.
