---
name: Refactor Domain — Advisory Refactoring Agent
description: Spec for a new refactor domain with an advisory-only agent that analyzes code quality, identifies code smells, and produces actionable refactoring plans. Includes a /refactor command, single-phase workflow, and service provider following the standard domain architecture.
---


# Refactor Domain — Advisory Refactoring Agent

## Overview

Introduce a new `refactor` domain at `src/byte/refactor/` containing an advisory-only agent that analyzes code for structural issues, code smells, and improvement opportunities. The agent produces actionable refactoring plans — concrete steps that can later be handed off to the coder agent for execution. It does **not** make edits itself.

## Domain Structure

```
src/byte/refactor/
├── __init__.py                          # Public API exports (lazy imports)
├── service_provider.py                  # Registers agent, command, workflow
├── agents/
│   └── refactor_agent_node.py           # Advisory refactoring agent
├── commands/
│   └── refactor_command.py              # /refactor slash command
└── workflows/
    └── refactor_workflow.py             # Single-phase workflow
```

No `tools/`, `schemas.py`, `config.py`, `events.py`, or `models.py` needed for v1. The agent reuses existing tools (file reading, ripgrep search, LSP queries).

---

## Components

### 1. `RefactorAgentNode` (`agents/refactor_agent_node.py`)

Extends `BaseAgentNode`. Follows the same pattern as `SpecCreatorAgentNode` — single-phase, conversational agent with specialized prompts.

**Methods to implement:**

- **`boot(goto=EndNode)`** — Accept a `goto` parameter (defaults to `EndNode`). Store as `self.goto = Str.class_to_snake_case(goto)`.

- **`get_model()`** — Resolve model via `LLMService.get_model(self.name)`. Returns `tuple[ModelSchema, dict]`.

- **`get_system_template()`** — The agent's specialization lives here:
  - `Leaves.Preamble(role=...)` — Role should be: *"Act as an expert code quality analyst specializing in refactoring. Your job is to analyze code for structural issues, code smells, and improvement opportunities, and produce actionable refactoring plans."*
  - `Leaves.OperatingPrinciples()`
  - `Leaves.CommunicationStyle(verbose=True)` — Verbose since the agent's value is in detailed analysis.
  - `Leaves.WorkflowConstraints([...])` — Constraints should include:
    - Analyze code structure, complexity, coupling, and cohesion
    - Identify code smells: duplication, long methods, god classes, tight coupling, feature envy, etc.
    - Produce a prioritized list of concrete refactoring steps
    - Each step must describe **what** to refactor, **why** it's a problem, and **how** to fix it (rename, extract, move, simplify, inline, etc.)
    - Include affected files/classes/functions for each step
    - Flexible scope: handle file-level, module-level, or project-level analysis based on the user's request
    - Advisory only — do NOT invoke file-editing tools; only read and search
  - `Section.end()`

- **`get_user_template()`** — Include `Leaves.UserRequest()`. No "tool operations are applied immediately" notice since this agent is advisory-only.

- **`get_context_template()`** — Include:
  - `Leaves.SkillsLoaded()`
  - `Leaves.ToolsLoaded()`
  - `Leaves.ReferenceMaterials()`
  - `Leaves.ProjectEnvironment()`
  - `Leaves.FileContext()`
  - `Leaves.WorkflowPending()`
  - `Leaves.Epilogue()`

- **`__call__(state, config)`** — Follow the standard pattern (mirrors `SpecCreatorAgentNode`):
  1. Generate agent state via `self.generate_agent_state(state, config)`
  2. Create runnable via `self.create_runnable(prompt_assembler)`
  3. Generate prompt via `self.generate_prompt(prompt_assembler)`
  4. Loop: invoke runnable → route tool calls if present → re-prompt if workflow incomplete

**What it does NOT include:**
- No custom `get_tools()` override — uses the standard tool set
- No custom `get_prompt()` override — default fragment ordering is correct
- No schemas or structured output enforcement

### 2. `RefactorCommand` (`commands/refactor_command.py`)

Extends `Command`. Invoked via `/refactor` in the TUI.

- **`name`** property → returns `"refactor"`
- **`parser`** — `ByteArgumentParser` with:
  - `prog="refactor"`
  - `description="Analyze code for structural issues, code smells, and produce actionable refactoring plans"`
  - No additional arguments for v1 — scope is inferred from the user's natural language request via `raw_args`
- **`boot()`** — Resolve workflow dispatch dependencies from the container
- **`execute(args, raw_args)`** — Dispatch `RefactorWorkflow` with the user's request as input

### 3. `RefactorWorkflow` (`workflows/refactor_workflow.py`)

Single-phase workflow. The agent handles analysis conversationally in one pass.

- **Graph structure:** `StartNode → RefactorAgentNode → ToolNode (loop) → EndNode`
- **No `tool_choice` enforcement** — the agent freely decides when and how to use tools
- **No custom state** — uses `BaseState` directly
- **No multi-phase orchestration** — the intelligence lives in the agent's prompts

### 4. `RefactorServiceProvider` (`service_provider.py`)

Extends `ServiceProvider`. Pure wiring — no custom logic.

```python
class RefactorServiceProvider(ServiceProvider):
    def agents(self):
        return [RefactorAgentNode]

    def commands(self):
        return [RefactorCommand]

    def workflows(self):
        return [RefactorWorkflow]
```

- No `services()` override — no domain-specific services
- No `boot()` override — no event listeners or cross-domain wiring
- No `tools()` override — reuses existing tools
- Must be registered in `Application.configure()` alongside existing providers

### 5. `__init__.py`

Public API exports using the lazy `_dynamic_imports` + `import_attr` pattern (mirrors `src/byte/coder/__init__.py`).

**Exports:**
- `RefactorAgentNode`
- `RefactorCommand`
- `RefactorServiceProvider`
- `RefactorWorkflow`

---

## Registration

Add `RefactorServiceProvider` to the application's provider list in `Application.configure()` alongside the existing providers (e.g., `CoderServiceProvider`, `SpecsServiceProvider`).

---

## Data Flow

1. User invokes `/refactor <request>` in the TUI
2. `RefactorCommand.execute()` dispatches `RefactorWorkflow` with the user's request
3. Workflow routes to `RefactorAgentNode`
4. Agent uses existing tools (file reading, ripgrep, LSP) to gather context about the target code
5. Agent loops through `ToolNode` as needed to read files and search for patterns
6. Agent produces the final actionable refactoring plan
7. Workflow routes to `EndNode`, plan is displayed to the user

---

## Error Handling

- **No file mutations** — advisory-only agent only reads and searches, no risk of partial writes
- **Standard tool errors** — file read/search failures are surfaced to the agent, which can retry or adjust
- **LLM failures** — handled by existing `BaseAgentNode` infrastructure (retry logic, timeout handling)
- **No domain-specific exceptions** — no `exceptions.py` needed for v1

---

## Testing

Tests live under `src/tests/refactor/`.

### Test Files

- **`test_refactor_agent_node.py`** — Verify the agent produces actionable refactoring plans:
  - Agent receives code with known issues → produces a plan with concrete steps
  - Agent handles file-level, module-level, and project-level requests
  - Agent does NOT invoke file-editing tools (advisory-only behavior)
  - Uses VCR cassettes (`pytest-recording`) for deterministic LLM interactions

- **`test_refactor_command.py`** — Verify the `/refactor` command:
  - `boot()` correctly resolves dependencies
  - Arguments parse correctly
  - Workflow is dispatched properly

- **`test_refactor_workflow.py`** — Verify the workflow graph:
  - Wires correctly: `StartNode → RefactorAgentNode → ToolNode (loop) → EndNode`
  - Runs to completion with a valid request

### Testing Conventions

- Use `pytest-asyncio` for all async tests
- Use `pytest-mock` (not `unittest.mock`) for mocking
- Use `pytest-recording` (VCR cassettes) for all LLM interactions
- Generate coverage reports on every test run

---

## Key Design Decisions

1. **Advisory only** — The agent analyzes and plans but never edits. This keeps the error surface minimal and creates a clean separation from the coder agent.
2. **Single-phase workflow** — No multi-phase orchestration. The LLM handles varying complexity naturally through prompt design. Phases can be added later if needed.
3. **No new tools** — Existing file reading, search, and LSP tools are sufficient for code analysis. Custom analysis tools (complexity metrics, dependency graphs) can be added in a future iteration.
4. **Free-form output** — The refactoring plan is produced as actionable prose, not a structured schema. This maximizes flexibility across different refactoring scenarios. Structured output (Pydantic schemas) can be added later if programmatic handoff to the coder agent is desired.
5. **Mirrors `SpecCreatorAgentNode` pattern** — The implementation closely follows the spec creator agent, which is the simplest existing agent pattern. This minimizes new code and ensures consistency.

