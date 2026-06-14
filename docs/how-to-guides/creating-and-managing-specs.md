# Create & Manage Specs

**Category**: How-to Guide

This guide shows you how to create, structure, and execute specs in Byte. Specs are implementation plans that decompose large features into executable tasks. You'll learn three approaches to creating specs, how to organize them on disk, and how to execute them step by step.

## Prerequisites

- Byte installed on your system
- Basic understanding of YAML (for frontmatter)
- Familiarity with markdown formatting
- A `.byte/specs/` directory for storing specs (created automatically)

## Step 1: Understand What Specs Are

A spec is a structured implementation plan that breaks a feature or refactoring work into concrete tasks. Every spec consists of:

- **SPEC.md** — The top-level specification file with YAML frontmatter and detailed instructions
- **tasks/** — A subdirectory containing individual task files (one per file), each with metadata and execution instructions

Specs live in `.byte/specs/<topic>/` where `<topic>` is a descriptive directory name. When you execute a spec, Byte runs the Coder workflow for each task sequentially, loading the task's designated files and confirming completion before moving to the next task.

Specs solve a real problem: large features that require multiple focused passes through code. Instead of trying to build everything in one coder run, specs let you define discrete, reviewable units of work.

## Step 2: Understand Spec Directory Structure

Each spec occupies its own directory with a required `SPEC.md` file and optional `tasks/` subdirectory:

```
.byte/specs/
└── my-feature/
    ├── SPEC.md                  (required)
    └── tasks/                   (optional, created during spec generation)
        ├── setup-database.md
        ├── create-api-endpoints.md
        └── add-validation.md
```

- **SPEC.md** — Contains YAML frontmatter (name, description, optional reference_files) and the full specification text
- **tasks/\*.md** — Individual task files with frontmatter (id, order, status, notes, files) and task content

The tasks directory is created automatically when the Spec Creator Agent generates tasks. You can organize as many tasks as needed.

## Step 3: Create a Spec With /spec:init (Thorough Path)

The `/spec:init` command guides you through a comprehensive spec creation workflow. Use this when you want to deeply explore the design space before committing to an approach.

**Step 3.1: Invoke the command**

```bash
/spec:init Build a real-time notification system for the dashboard
```

**Step 3.2: Understand the workflow phases**

The `/spec:init` workflow runs through these phases:

1. **select-skills** — System identifies relevant skills based on your request
2. **capture-intent** — The Spec Creator Agent learns about your feature: goals, problem it solves, expected outcome
3. **clarify** — One-by-one questions to understand purpose, constraints, and success criteria
4. **propose** — Agent presents 2–3 design approaches with trade-offs and a recommendation
5. **present-design** — Agent walks through the recommended design in detail: architecture, components, data flow, error handling, testing
6. **create-spec** — Agent generates the SPEC.md file in `.byte/specs/`

At each phase, you guide the conversation. If an approach isn't working, say so. If you want to skip ahead (e.g., you already know the design), tell the agent.

**Step 3.3: Review the generated spec**

When the workflow completes, the spec is saved to `.byte/specs/<topic>/SPEC.md`. You can now:

- Execute it with `/spec:execute <topic>`
- Edit the spec file manually to refine it
- Create tasks by running `/spec:quick <topic>` (see Step 5)

## Step 4: Create a Quick Spec With /spec:quick (Fast Path)

Use `/spec:quick` when you already know what needs to be built and just need to formalize it into a spec. This skips the lengthy design discussion and goes straight to clarification and spec generation.

**Step 4.1: Invoke the command**

```bash
/spec:quick Add email notifications to the user settings panel
```

**Step 4.2: Understand the workflow phases**

The `/spec:quick` workflow runs through:

1. **create-instruction** — System synthesizes a clear instruction from your request and conversation history
2. **clarify** — One or two clarifying questions if needed (skipped if the request is already clear)
3. **create-spec** — Agent generates SPEC.md
4. **create-tasks** — Agent generates individual task files in `tasks/`

This is much faster than `/spec:init` because it assumes you know what you want and skips the exploratory phases.

**Step 4.3: The generated spec and tasks**

When complete, you have:

- `.byte/specs/<topic>/SPEC.md` — The specification
- `.byte/specs/<topic>/tasks/*.md` — Ready-to-execute tasks

You can immediately run `/spec:execute <topic>` to start working through them.

## Step 5: Create a Refactoring Spec With /spec:refractor (Specialized Path)

Use `/spec:refractor` when you want to refactor code but need help identifying what to refactor and how. This workflow analyzes your codebase and recommends refactoring opportunities.

**Step 5.1: Invoke the command**

```bash
/spec:refractor The authentication module is getting complex and hard to test
```

**Step 5.2: Understand the workflow phases**

The `/spec:refractor` workflow runs through:

1. **select-skills** — System identifies relevant skills
2. **analyze** — Agent reviews the loaded files and recommends refactoring opportunities with specific examples
3. **clarify** — One-by-one questions to understand which recommendations you want to pursue and what constraints apply
4. **create-spec** — Agent generates SPEC.md
5. **create-tasks** — Agent breaks down the refactoring into executable tasks

This workflow is purpose-built for refactoring because it starts by analyzing code and proposing improvements, rather than asking you to describe the problem.

**Step 5.3: The generated spec and tasks**

Same as `/spec:quick` — you get a spec and ready-to-execute tasks.

## Step 6: Understand Spec File Structure

A spec file contains YAML frontmatter and markdown instructions. Here's the structure:

```yaml
---
name: Build Real-Time Notifications
description: Add WebSocket-based notifications to the dashboard with fallback polling
reference_files:
  - src/api/websocket.py
  - docs/architecture.md
---

# Real-Time Notification System

## Overview

This spec describes the implementation of a real-time notification system...

## Architecture

The system uses WebSocket connections with Redis pub/sub for message broadcasting...

## Database Schema

...

## API Endpoints

...
```

**Frontmatter fields:**

- `name` (required) — Short, descriptive spec name
- `description` (required) — One-line summary of what the spec covers
- `reference_files` (optional) — Array of file paths that provide context (loaded but not edited)

The markdown body is the full specification text. Write it as clearly and completely as you'd want to read it.

## Step 7: Understand Task File Structure

Tasks are individual markdown files in `.byte/specs/<topic>/tasks/` with YAML frontmatter and content. Here's the structure:

```yaml
---
id: setup-database-schema
order: 1
status: pending
notes:
  - Use PostgreSQL constraints to enforce data integrity
  - Create migration script with rollback
files:
  reference:
    - docs/database-schema.md
  create:
    - src/migrations/001_notification_tables.sql
  edit:
    - src/models/notification.py
    - src/db/schema.py
---

# Set Up Database Schema

Create the database tables and relationships needed for the notification system.

## Tables

- `notifications` — Stores user notifications
- `notification_preferences` — User opt-in/opt-out settings
- `notification_channels` — Email, SMS, push, etc.

## Constraints

All timestamps must use UTC. Foreign keys must be NOT NULL...
```

**Frontmatter fields:**

- `id` (required) — Unique task identifier (e.g., `setup-database-schema`)
- `order` (required) — Numeric sequence number (1, 2, 3, etc.)
- `status` (required) — One of: `pending`, `in_progress`, `blocked`, `completed`
- `notes` (optional) — Array of additional notes or observations for this task
- `files` (optional) — Files to load during execution:
  - `reference` — Files to review but not modify
  - `create` — Files to be created
  - `edit` — Files to be edited

The markdown body is the task description. Write it as a focused set of instructions for that specific unit of work.

## Step 8: Execute a Spec With /spec:execute

Once you have a spec and tasks, execute them step by step.

**Step 8.1: Invoke the command**

```bash
/spec:execute my-feature
```

Where `my-feature` matches the directory name in `.byte/specs/my-feature/`.

**Step 8.2: Understand the execution flow**

When you run `/spec:execute`, Byte:

1. **Loads the spec's tasks** from the `tasks/` subdirectory, sorted by `order`
2. **For each task** (in order):
   - Skips it if status is `completed`
   - Loads the task's designated files (reference and edit/create files)
   - Runs the Coder workflow with the task's content as the instruction
   - Pauses for your confirmation before moving to the next task
3. **Resumes from where you left off** on subsequent runs (completed tasks are skipped)

Each task runs in its own isolated Coder workflow with only the files it needs. This keeps focus tight and changes reviewable.

**Step 8.3: Approve task completion**

After the Coder Agent completes work on a task, you see:

```
Validate task completion [Y/n]:
```

- Type `y` (or just press Enter) to mark the task completed and move to the next one
- Type `n` to retry the task without marking it complete

Your choice is persisted. On the next `/spec:execute` run, completed tasks are skipped.

## Step 9: Resume Execution

If you run `/spec:execute` on a spec with some tasks already completed, only the pending tasks are executed.

**Example:**

You run `/spec:execute my-feature` and complete tasks 1 and 2. You then run `/spec:execute my-feature` again. Byte skips tasks 1 and 2 and starts with task 3.

This is the intended workflow — you can pause, review, iterate, and resume without losing progress.

## Step 10: Manually Edit Specs and Tasks

You can manually edit existing SPEC.md and task files directly. This is useful when you want to refine a generated spec, adjust task descriptions, or update task status.

Open any spec file or task file in your editor and modify the content as needed. Changes to frontmatter fields (like `status`, `notes`, `files`) will be recognized the next time you run `/spec:execute`. Changes to the markdown body will be reflected in the next task execution.

## Example 1: Quick Spec for a Simple Feature

You decide to add a search page to your app. You know roughly what it needs, so you use `/spec:quick`:

```bash
/spec:quick Add search page with filters and results pagination
```

The agent asks one clarifying question about pagination style. You answer. The agent generates:

- `.byte/specs/search-page/SPEC.md` — Full specification
- `.byte/specs/search-page/tasks/create-search-endpoint.md` — Task 1
- `.byte/specs/search-page/tasks/build-search-ui.md` — Task 2
- `.byte/specs/search-page/tasks/add-pagination.md` — Task 3

You then run:

```bash
/spec:execute search-page
```

Byte runs the Coder workflow for each task, loading the designated files and confirming completion before moving to the next.

## Example 2: Refactoring Spec for a Troubled Module

Your authentication module has become a maintenance headache. You use `/spec:refractor`:

```bash
/spec:refractor The auth module is too tightly coupled and hard to test
```

The agent analyzes the auth code, recommends breaking it into smaller services, and asks which recommendations you want to pursue. You select a few. The agent generates:

- `.byte/specs/refactor-auth/SPEC.md` — Refactoring plan
- `.byte/specs/refactor-auth/tasks/extract-token-service.md`
- `.byte/specs/refactor-auth/tasks/extract-permission-checker.md`
- `.byte/specs/refactor-auth/tasks/update-tests.md`

You execute them one by one, reviewing the refactored code as you go.

## Example 3: Deep Design with /spec:init

You're building a complex feature and want to explore the design space. You use `/spec:init`:

```bash
/spec:init Build a real-time collaborative editor for documents
```

The Spec Creator Agent asks about your goals, constraints, and success metrics. You discuss whether to use OT (Operational Transformation) or CRDT for conflict resolution. The agent proposes three architectures and recommends one. It walks through the design in detail. You approve it and the spec is generated.

This back-and-forth clarifies the design before you write any code.

## Common Workflows

### Scenario 1: Standard Feature with Spec Generation

```bash
/spec:quick Build a user profile page

# Agent generates spec and tasks

/spec:execute user-profile

# Complete each task, confirm completion, move to next
```

### Scenario 2: Refactoring Sprint

```bash
/spec:refractor The payment module needs better error handling and logging

# Agent analyzes and proposes refactoring steps

# You select which to pursue

/spec:execute refactor-payment

# Work through each refactoring task
```

### Scenario 3: Pausing and Resuming

```bash
/spec:execute my-feature

# Complete tasks 1–3, then stop for the day

# Next day:
/spec:execute my-feature

# Skips completed tasks 1–3, starts with task 4
```

## Next Steps

Now that you understand specs, you can:

- **Create your first spec** using any of the three approaches (`/spec:init`, `/spec:quick`, `/spec:refractor`)
- **Execute specs** to break down large features into focused, reviewable work
- **Combine specs with the Constitution** — Define coding standards that guide task execution

For deeper understanding of how specs integrate with Byte's overall workflow, see the Architecture Overview.
