---
files:
  create:
  - src/byte/refactor/agents/refactor_agent_node.py
  edit: []
  reference:
  - src/byte/specs/agents/spec_creator_agent_node.py
  - src/byte/coder/agents/coder_agent_node.py
id: implement-refactor-agent-node
notes:
- Copy the __call__ loop verbatim from SpecCreatorAgentNode — do not invent a new
  pattern.
- verbose=True on CommunicationStyle because detailed analysis is the agent's core
  value.
- No get_tools() override — the standard tool set (file reading, ripgrep, LSP) is
  sufficient.
- No structured output / schema enforcement for v1.
order: 2
status: pending
---
## Implement `RefactorAgentNode`

Fill in `src/byte/refactor/agents/refactor_agent_node.py` with the full agent implementation.

### Pattern to Follow

Mirror `SpecCreatorAgentNode` (`src/byte/specs/agents/spec_creator_agent_node.py`) exactly — same method signatures, same call order inside `__call__`, same prompt-assembly pattern.

### Class Definition

```python
class RefactorAgentNode(BaseAgentNode):
    name = "refactor_agent"
```

### Methods

#### `boot(goto=EndNode)`

```python
def boot(self, goto=EndNode):
    self.goto = Str.class_to_snake_case(goto)
```

#### `get_model()`

```python
def get_model(self) -> tuple[ModelSchema, dict]:
    llm_service: LLMService = self.app.make(LLMService)
    return llm_service.get_model(self.name)
```

#### `get_system_template()`

Build via the `Branch` / `Leaves` / `Section` API (same imports as `SpecCreatorAgentNode`):

```python
def get_system_template(self):
    return (
        Branch()
        .add(Leaves.Preamble(
            role=(
                "Act as an expert code quality analyst specializing in refactoring. "
                "Your job is to analyze code for structural issues, code smells, and "
                "improvement opportunities, and produce actionable refactoring plans."
            )
        ))
        .add(Leaves.OperatingPrinciples())
        .add(Leaves.CommunicationStyle(verbose=True))
        .add(Leaves.WorkflowConstraints([
            "Analyze code structure, complexity, coupling, and cohesion.",
            "Identify code smells: duplication, long methods, god classes, tight coupling, feature envy, etc.",
            "Produce a prioritized list of concrete refactoring steps.",
            "Each step must describe what to refactor, why it is a problem, and how to fix it (rename, extract, move, simplify, inline, etc.).",
            "Include affected files, classes, and functions for each step.",
            "Handle file-level, module-level, or project-level analysis based on the user's request.",
            "Advisory only — do NOT invoke file-editing tools; only read and search.",
        ]))
        .add(Section.end())
    )
```

#### `get_user_template()`

```python
def get_user_template(self):
    return Branch().add(Leaves.UserRequest())
```

No "tool operations are applied immediately" notice — this agent is read-only.

#### `get_context_template()`

```python
def get_context_template(self):
    return (
        Branch()
        .add(Leaves.SkillsLoaded())
        .add(Leaves.ToolsLoaded())
        .add(Leaves.ReferenceMaterials())
        .add(Leaves.ProjectEnvironment())
        .add(Leaves.FileContext())
        .add(Leaves.WorkflowPending())
        .add(Leaves.Epilogue())
    )
```

#### `__call__(state, config)`

Follow the exact loop structure from `SpecCreatorAgentNode`:

1. `prompt_assembler = self.generate_agent_state(state, config)`
2. `runnable = self.create_runnable(prompt_assembler)`
3. `prompt = self.generate_prompt(prompt_assembler)`
4. Loop:
   - Invoke runnable with prompt
   - If response has tool calls → route through `ToolNode`, re-prompt
   - If workflow is incomplete → continue loop
   - Otherwise → break and return final state

### Imports Required

Look at `SpecCreatorAgentNode` for the exact import list — `BaseAgentNode`, `EndNode`, `LLMService`, `ModelSchema`, `Branch`, `Leaves`, `Section`, `Str`.

### Verification

```bash
uv run python -c "from byte.refactor.agents.refactor_agent_node import RefactorAgentNode; print('OK')"
```
