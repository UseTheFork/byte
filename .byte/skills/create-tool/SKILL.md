---
name: create-tool
description: Documents the full process for creating a new LLM-invokable tool in the Byte project. Use this skill when creating, modifying, or understanding tools that extend BaseTool.
---


# Create Tool Guide

This skill documents the full process for creating a new LLM-invokable tool in the Byte project. Tools live in domain-specific `tools/` directories and extend `BaseTool`.

## Overview

A tool is an action the LLM can invoke during a conversation. Each tool has:

- A **name** — unique identifier used by the LLM to call the tool
- A **description** — tells the LLM when and how to use the tool
- An **input schema** — JSON Schema defining the tool's parameters
- A **`run()` method** — the async execution logic
- **Message formatters** — `format_tool_message()` (for the LLM) and optionally `format_tui_message()` (for the user)
- **Registration** in a domain's service provider

The base class is located at `src/byte/tools/base_tool.py`. Tools are executed at runtime by the `ToolNode` (`src/byte/node/nodes/tool_node.py`), which resolves them from `ToolRegistryService`.

---

## Tool File Structure

Each tool file lives in a domain's `tools/` directory:

```
src/byte/<domain>/tools/<tool_name>_tool.py
```

### 1. Imports

Standard imports used by all tools:

```python
from typing import override

from byte.tools import BaseTool, ToolResult
```

Add additional imports as needed:

- **Domain services** the tool uses (e.g., `from byte.files import FileService`)
- **`ToolRunException`** if you need to raise explicit tool errors (`from byte.tools.exceptions import ToolRunException`)
- **`BaseState`** if the tool reads from graph state (`from byte.orchestration import BaseState`)
- **Support utilities** for description formatting (e.g., `from byte.support import Boundary, BoundaryType, Section, SectionType`)

### 2. Tool Class

The class extends `BaseTool` and implements these required attributes and methods:

```python
class MyNewTool(BaseTool):
    name: str = "my_new_tool"
    description: str = "Description of what the tool does and when the LLM should use it."
    input_schema = {
        "type": "object",
        "properties": {
            "param_one": {
                "type": "string",
                "description": "Description of param_one.",
            },
            "param_two": {
                "type": "integer",
                "description": "Description of param_two.",
            },
            "optional_param": {
                "type": "string",
                "description": "Optional parameter with a default.",
            },
        },
        "required": ["param_one"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        """Format the result as a message returned to the LLM."""
        return result.result.get("content", "")

    @override
    async def run(
        self,
        param_one: str = "",
        param_two: int = 0,
        optional_param: str = "",
        **kwargs,
    ) -> ToolResult:
        # Resolve services from the container
        my_service = self.app.make(MyService)

        # Tool logic here
        output = await my_service.do_something(param_one)

        return ToolResult(
            result={"content": f"Done: {output}"}
        )
```

#### Class Attributes

| Attribute      | Type             | Description                                                                                     |
| -------------- | ---------------- | ----------------------------------------------------------------------------------------------- |
| `name`         | `str`            | Unique snake_case identifier. This is how the LLM references the tool and how it's registered.  |
| `description`  | `str`            | Clear description of what the tool does and when to use it. The LLM reads this to decide usage. |
| `input_schema` | `dict[str, Any]` | JSON Schema defining the tool's parameters. Must include `type`, `properties`, and `required`.  |

#### Key Methods

| Method                | Type        | Required | Description                                                                                           |
| --------------------- | ----------- | -------- | ----------------------------------------------------------------------------------------------------- |
| `run(**kwargs)`       | `async`     | **Yes**  | Core execution logic. Receives kwargs matching `input_schema` properties, plus `state` and `**kwargs`. |
| `format_tool_message` | `classmethod` | **Yes**  | Formats `ToolResult` into a string message sent back to the LLM.                                      |
| `format_tui_message`  | `classmethod` | No       | Formats `ToolResult` for display in the TUI. Defaults to calling `format_tool_message()`.             |

---

## The `run()` Method In Detail

The `run()` method is the tool's core logic. It is called by `BaseTool.invoke()`, which handles validation before delegating.

### Signature

```python
@override
async def run(
    self,
    param_one: str = "",
    param_two: int = 0,
    **kwargs,
) -> ToolResult:
```

- **Named parameters** must match the keys in `input_schema["properties"]`. Always provide default values.
- **`**kwargs`** is required — it captures additional arguments including `state`.

### Accessing Graph State

The current graph state (`BaseState`) is passed through `**kwargs` as `state`. Use it when the tool needs to read from the conversation or workflow state:

```python
async def run(self, **kwargs) -> ToolResult:
    state: BaseState = kwargs.get("state", {})
    messages = state.get("scratch_messages", [])
    # Use state data...
```

The state is passed by `BaseTool.invoke()`, which calls `await self.run(**args, state=state)`.

### Accessing the DI Container

All tools have access to the application container via `self.app`. Use it to resolve services:

```python
async def run(self, pattern: str = "", **kwargs) -> ToolResult:
    git_service = self.app.make(GitService)
    repo = await git_service.get_repo()
    # ...
```

### Returning Results

Always return a `ToolResult`:

```python
return ToolResult(
    result={"content": "The operation completed successfully."}
)
```

---

## ToolResult

`ToolResult` is the Pydantic model returned by all tools (defined in `src/byte/tools/schemas.py`):

```python
class ToolResult(BaseModel):
    success: bool = True
    result: dict
    extra: dict = Field(default_factory=dict)
```

| Field     | Type   | Default          | Description                                                                                                  |
| --------- | ------ | ---------------- | ------------------------------------------------------------------------------------------------------------ |
| `success` | `bool` | `True`           | Whether the tool execution succeeded. Set to `False` for logical failures (not exceptions).                  |
| `result`  | `dict` | (required)       | The tool's output data. By convention, use `{"content": "..."}` for text results.                            |
| `extra`   | `dict` | `{}` (empty)     | Extra data merged directly into the graph state update. Use this to pass data back into the workflow state.   |

### Using `extra` to Update Graph State

The `ToolNode` merges `extra` into the graph state update after tool execution:

```python
# In ToolNode.__call__:
if tool_result.extra:
    merged_extra.update(tool_result.extra)
# ...
update = {"scratch_messages": outputs, **merged_extra}
```

Use `extra` when a tool needs to write data back into the LangGraph state beyond the tool message. For example:

```python
return ToolResult(
    result={"content": "Plan created successfully."},
    extra={"plan": plan_data},  # This gets merged into the graph state
)
```

---

## Message Formatting

### `format_tool_message(result: ToolResult) -> str`

**Required.** This classmethod formats the `ToolResult` into a string that gets sent back to the LLM as a `ToolMessage`. The LLM reads this to understand what happened.

```python
@classmethod
def format_tool_message(cls, result: ToolResult) -> str:
    return result.result.get("content", "")
```

This is the most common pattern. For tools with richer output, you can format a more detailed message:

```python
@classmethod
def format_tool_message(cls, result: ToolResult) -> str:
    data = result.result
    return f"Found {data['count']} matches:\n{data['matches']}"
```

### `format_tui_message(result: ToolResult) -> str`

**Optional.** This classmethod formats the `ToolResult` for display in the TUI (what the user sees). By default, it delegates to `format_tool_message()`:

```python
@classmethod
def format_tui_message(cls, result: ToolResult) -> str:
    return cls.format_tool_message(result)
```

Override this when the user should see a different (typically shorter or friendlier) message than what the LLM receives:

```python
@classmethod
def format_tui_message(cls, result: ToolResult) -> str:
    # Show a concise summary to the user
    return f"Edited {result.result.get('file_path', 'file')}"
```

The `ToolNode` calls `format_tui_message()` when updating the TUI, and `format_tool_message()` when constructing the `ToolMessage` sent back to the LLM.

---

## Error Handling

### Exception Hierarchy

All tool exceptions inherit from `ToolException` (defined in `src/byte/tools/exceptions.py`):

```
ToolException (base)
├── ToolRunException        — Errors during tool execution
├── ToolValidationException — Input validation failures (auto-raised by invoke())
└── ToolNotFoundException   — Tool not found in registry (raised by ToolNode)
```

### Raising Errors in `run()`

Use `ToolRunException` for explicit errors during execution:

```python
from byte.tools.exceptions import ToolRunException

async def run(self, pattern: str = "", **kwargs) -> ToolResult:
    try:
        result = await some_operation(pattern)
        return ToolResult(result={"content": result})
    except Exception as e:
        raise ToolRunException(f"Error performing operation: {e!s}") from e
```

**Key rules:**

- Raise `ToolRunException` for known failure cases you want to communicate to the LLM
- Unhandled exceptions in `run()` are automatically caught by `BaseTool.invoke()` and wrapped in `ToolRunException`
- `ToolValidationException` is raised automatically by `invoke()` when required fields from `input_schema` are missing — you don't need to handle this
- All `ToolException` subclasses are caught by `ToolNode` and returned to the LLM as error messages

---

## Registration

After creating the tool file, register it in the domain's service provider.

### Step 1: Add to the domain's `ServiceProvider.tools()`

In the domain's `service_provider.py`, import the tool and add it to the `tools()` list:

```python
from byte.my_domain import MyNewTool
from byte.tools import BaseTool

class MyDomainServiceProvider(ServiceProvider):
    def tools(self) -> List[Type[BaseTool]]:
        return [
            # ... existing tools ...
            MyNewTool,
        ]
```

This is all that's needed — the base `ServiceProvider.register_tools()` method iterates the list and calls `ToolRegistryService.register_tool()` for each class.

### Step 2: Export from the domain's `__init__.py`

Add the tool to the domain's public API so it can be imported cleanly:

```python
# In TYPE_CHECKING block:
from byte.my_domain.tools.my_new_tool import MyNewTool

# In __all__:
__all__ = (
    # ... existing ...
    "MyNewTool",
)

# In _dynamic_imports (keep-sorted):
_dynamic_imports = {
    # keep-sorted start
    # ... existing ...
    "MyNewTool": "tools.my_new_tool",
    # keep-sorted end
}
```

> **IMPORTANT**: Entries in `_dynamic_imports` must remain sorted alphabetically between the `# keep-sorted start` and `# keep-sorted end` comments.

---

## Naming Conventions

| Item            | Convention                   | Example                   |
| --------------- | ---------------------------- | ------------------------- |
| File name       | `<name>_tool.py`             | `search_web_tool.py`      |
| Class name      | `<Name>Tool`                 | `SearchWebTool`           |
| `name` field    | `snake_case` string          | `"search_web"`            |
| Tool directory  | `src/byte/<domain>/tools/`   | `src/byte/web/tools/`     |

---

## Quick Reference: Files to Touch

When creating a new tool, you will modify/create these files:

1. **CREATE** `src/byte/<domain>/tools/<name>_tool.py` — The tool implementation
2. **EDIT** `src/byte/<domain>/__init__.py` — Add exports and dynamic import entry
3. **EDIT** `src/byte/<domain>/service_provider.py` — Add to `tools()` list

---

## Complete Example: A Simple Tool

Here is a complete minimal tool following all conventions:

```python
# src/byte/web/tools/search_web_tool.py
from byte.tools import BaseTool, ToolResult


class SearchWebTool(BaseTool):
    name: str = "search_web"
    description: str = "Search the web for information on a given query."
    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query.",
            },
        },
        "required": ["query"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    async def run(self, query: str = "", **kwargs) -> ToolResult:
        search_service = self.app.make(SearchService)
        results = await search_service.search(query)
        return ToolResult(result={"content": results})
```

## Complete Example: A Tool Using State and Extra

```python
# src/byte/memory/tools/create_plan_tool.py
from byte.orchestration import BaseState
from byte.tools import BaseTool, ToolResult


class CreatePlanTool(BaseTool):
    name: str = "create_plan"
    description: str = "Create a step-by-step plan for the current task."
    input_schema = {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of plan steps.",
            },
        },
        "required": ["steps"],
    }

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")

    @classmethod
    def format_tui_message(cls, result: ToolResult) -> str:
        # Show a shorter message to the user
        return "Plan created."

    async def run(self, steps: list[str] = [], **kwargs) -> ToolResult:
        state: BaseState = kwargs.get("state", {})
        # Read from state if needed
        existing = state.get("plan", [])

        plan_service = self.app.make(PlanService)
        plan = await plan_service.create(steps)

        return ToolResult(
            result={"content": f"Plan created with {len(steps)} steps."},
            extra={"plan": plan},  # Merged into graph state by ToolNode
        )
```

