---
files:
  create:
  - src/byte/refactor/commands/refactor_command.py
  edit: []
  reference:
  - src/byte/specs/commands/specs_command.py
  - src/byte/coder/commands/coder_command.py
id: implement-refactor-command
notes:
- No extra CLI arguments for v1 — raw_args carries the full user request.
- boot() must resolve all dispatch dependencies through self.app.make(), never direct
  instantiation.
- Follow the exact dispatch pattern used by CoderCommand or SpecsCommand — do not
  invent a new one.
order: 3
status: pending
---
## Implement `RefactorCommand`

Fill in `src/byte/refactor/commands/refactor_command.py`.

### Pattern to Follow

Mirror the simplest existing command — look at the spec command (`src/byte/specs/commands/specs_command.py`) for the exact structure: `name`, `parser`, `boot()`, `execute()`.

### Class Definition

```python
class RefactorCommand(Command):
    @property
    def name(self) -> str:
        return "refactor"
```

### Parser

```python
@property
def parser(self) -> ByteArgumentParser:
    p = ByteArgumentParser(
        prog="refactor",
        description="Analyze code for structural issues, code smells, and produce actionable refactoring plans",
    )
    return p
```

No additional positional or optional arguments for v1 — scope is driven entirely by the user's natural-language request passed via `raw_args`.

### `boot()`

Resolve `RefactorWorkflow` (and any dispatch dependencies the workflow requires) from the container. Look at an existing command's `boot()` to see how workflow dispatch is wired up.

```python
def boot(self):
    # resolve dispatch dependencies via self.app.make(...)
    ...
```

### `execute(args, raw_args)`

Dispatch `RefactorWorkflow` using the raw user input as the workflow's request payload:

```python
def execute(self, args, raw_args: str):
    # dispatch RefactorWorkflow with raw_args as the user request
    ...
```

### Imports Required

`Command`, `ByteArgumentParser`, `RefactorWorkflow` (import from the workflows module), plus whatever dispatch helpers existing commands use.

### Verification

```bash
uv run python -c "from byte.refactor.commands.refactor_command import RefactorCommand; print('OK')"
```
