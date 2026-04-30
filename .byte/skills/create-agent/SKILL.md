---
name: create-agent
description: Guide for creating new agent nodes in the Byte project. Use when creating a new agent under src/byte/node/agents/, or when you need to understand how agent nodes are structured, registered, and wired into the system.
---

# Create Agent Guide

This skill documents the full process for creating a new agent node in the Byte project. Agents live in `src/byte/node/agents/` and extend `BaseAgentNode`.

## Overview

An agent node is an LLM-powered node in the LangGraph workflow. Each agent has:

- A **prompt** (system + user templates assembled into a `ChatPromptTemplate`)
- A **model** (resolved via `LLMService`)
- **Tools** (optional, bound to the model at runtime)
- A **message type** (inner class on `ByteAIMessage` for casting agent responses)
- **Registration** in the service provider and `__init__.py` exports

---

## Agent File Structure

Each agent file follows this layout:

```
src/byte/node/agents/<name>_agent_node.py
```

### 1. Imports

Standard imports used by all agents:

```python
from typing import Literal, Type

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from langgraph.types import Command

from byte.development import RecordResponseService
from byte.llm import LLMService, ModelSchema
from byte.node import BaseAgentNode, BaseNode, ByteAIMessage
from byte.node.messages import BaseAIMessage
from byte.node.nodes import EndNode
from byte.orchestration import BaseState
from byte.support import Section, SectionType, Str
from byte.support.utils import extract_content_from_message
```

Add additional imports for:

- **Tools** the agent will use (e.g., `from byte.files import EditFileTool`)
- **`Boundary` / `BoundaryType`** if the prompt includes example blocks (`from byte.support import Boundary, BoundaryType`)
- **`State`** if tools are conditionally included based on state (`from byte.support import State`)

### 2. Module-Level Prompt Templates

Define three module-level variables **before** the class:

#### `user_template` — A `list[str]` defining the user message

- Starts with `"{modified_messages}"` and `"{user_request}"` placeholders
- Uses `Section.start(SectionType.X)` / `Section.end()` to wrap logical blocks
- Common section types: `OPERATING_CONSTRAINTS`, `TASK`, `WORKFLOW`, `RESPONSE_FORMAT`, `COMMUNICATION_STYLE`, `EXAMPLES`
- Ends with `"{operating_principles}"`
- Optionally includes `Section.important(...)` for critical instructions
- Use `Boundary.open(BoundaryType.EXAMPLE)` / `Boundary.close(BoundaryType.EXAMPLE)` for example blocks

#### `system_template` — A `list[str]` defining the system message

- Always starts with `"{preamble}"`
- Contains a `Section.start(SectionType.ROLE)` / `Section.end()` block with the agent's role description
- Always ends with `"{available_skills}"`

#### `prompt` — A `ChatPromptTemplate`

This is **always** the same structure across all agents:

```python
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_message}"),
        ("user", "{user_message}"),
        ("placeholder", "{scratch_messages}"),
        ("user", "{context_message}"),
    ]
)
```

> **IMPORTANT**: Do NOT modify the `prompt` structure. It is consistent across all agents.

### 3. Agent Class

The class extends `BaseAgentNode` and implements these required methods:

```python
class MyNewAgentNode(BaseAgentNode):
    def boot(
        self,
        goto: Type[BaseNode] = EndNode,
        **kwargs,
    ):
        self.goto = Str.class_to_snake_case(goto)

    @property
    def message_type(self) -> Type[BaseAIMessage]:
        return ByteAIMessage.MyNewAgentMessage

    def get_model(self) -> tuple[ModelSchema, dict]:
        llm_service = self.app.make(LLMService)
        return llm_service.get_model(self.name)

    def get_prompt(self):
        return prompt

    def get_user_template(self):
        return user_template

    def get_system_template(self):
        return system_template

    def get_tools(self, state: BaseState):
        return [
            # List tool classes here (not instances)
        ]

    async def __call__(
        self,
        state: BaseState,
        *,
        config: RunnableConfig,
    ) -> Command[Literal["routing_node"]]:

        agent_state, config = await self.generate_agent_state(state, config)
        runnable = self.create_runnable(state)
        record_response_service = self.app.make(RecordResponseService)

        result = await runnable.ainvoke(agent_state, config=config)
        self.app.dispatch_task(
            record_response_service.record_response(agent_state, runnable, self.name, config),
        )

        route_tool_call = self.route_tool_calls(result)
        if route_tool_call is not None:
            return route_tool_call

        msg = extract_content_from_message(result)
        return self.route_to(self.goto, {"scratch_messages": ByteAIMessage.MyNewAgentMessage(content=msg)})
```

#### Key method details

| Method                             | Purpose                                                                                                                              |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `boot(goto)`                       | Sets routing target. `goto` is a `BaseNode` subclass, converted to snake_case via `Str.class_to_snake_case()`. Default is `EndNode`. |
| `message_type`                     | Property returning the `ByteAIMessage` inner class for this agent. Used by `route_tool_calls()` to cast results.                     |
| `get_model()`                      | Resolves the model via `LLMService.get_model(self.name)`. The `self.name` is auto-derived from the class name (snake_case).          |
| `get_prompt()`                     | Returns the module-level `prompt` variable.                                                                                          |
| `get_user_template()`              | Returns the module-level `user_template` variable.                                                                                   |
| `get_system_template()`            | Returns the module-level `system_template` variable.                                                                                 |
| `get_tools(state)`                 | Returns a list of **tool classes** (not instances). Can be conditional based on `state`. Return `[]` if no tools are needed.         |
| `get_enforcement()`                | Optional. Returns a `list[str]` of enforcement rules appended to the prompt. Default returns `[]`.                                   |
| `filter_message_history(messages)` | Optional. Override to filter scratch messages before they reach the LLM. Default returns all messages unmodified.                    |
| `__call__(state, config)`          | Main execution. Always returns `Command[Literal["routing_node"]]`.                                                                   |

#### `__call__` pattern

The `__call__` method follows this standard sequence:

1. `generate_agent_state(state, config)` — Assembles the prompt state
2. `create_runnable(state)` — Builds the LLM chain (prompt | model with tools)
   - Pass `"any"` as second arg to force tool use: `self.create_runnable(state, "any")`
3. `runnable.ainvoke(agent_state, config=config)` — Invoke the LLM
4. `record_response_service.record_response(...)` — Dispatch recording as background task
5. `route_tool_calls(result)` — If the model returned tool calls, route to `tool_node`
6. Otherwise, extract content and `route_to(self.goto, ...)` with the message in `scratch_messages`

#### Optional: Conditional tools

Tools can be conditionally included based on state:

```python
def get_tools(self, state: BaseState):
    if not State.has_plan(state):
        return [CreatePlanTool]
    else:
        return [EditFileTool, CompleteStepTool]
```

#### Optional: Custom state in `__call__`

Some agents resolve additional services and pass extra data to `generate_agent_state`:

```python
commit_service = self.app.make(CommitService)
request = await commit_service.build_commit_prompt()
agent_state, config = await self.generate_agent_state(state, config, request)
```

---

## Registration Checklist

After creating the agent file, complete these wiring steps:

### Step 1: Add message type to `src/byte/node/messages.py`

Add a new inner class to `ByteAIMessage`:

```python
class ByteAIMessage:
    # ... existing messages ...

    class MyNewAgentMessage(BaseAIMessage):
        agent_name: str = "My New Agent"
```

- `agent_name` is the human-readable name shown in the TUI
- Set `mask: bool = True` if the agent's messages should be hidden from the user (e.g., commit agent)

### Step 2: Add to `src/byte/node/agents/__init__.py`

Add the import, export, and dynamic import entry:

```python
# In TYPE_CHECKING block:
from byte.node.agents.my_new_agent_node import MyNewAgentNode

# In __all__:
__all__ = (
    # ... existing ...
    "MyNewAgentNode",
)

# In _dynamic_imports (keep-sorted):
_dynamic_imports = {
    # keep-sorted start
    # ... existing ...
    "MyNewAgentNode": "my_new_agent_node",
    # keep-sorted end
}
```

> **IMPORTANT**: Entries in `_dynamic_imports` must remain sorted alphabetically between the `# keep-sorted start` and `# keep-sorted end` comments.

### Step 3: Add to `src/byte/node/service_provider.py`

Import the agent and add it to the `agents()` list:

```python
from byte.node.agents import MyNewAgentNode

class NodeServiceProvider(ServiceProvider):
    def agents(self) -> List[Type[BaseAgentNode]]:
        return [
            # keep-sorted start
            # ... existing ...
            MyNewAgentNode,
            # keep-sorted end
        ]
```

> **IMPORTANT**: Entries in the `agents()` list must remain sorted alphabetically between the `# keep-sorted start` and `# keep-sorted end` comments.

Agents are registered with `self.app.bind(agent_class)` — this is **transient** (new instance per resolution).

### Step 4: Wire into a workflow (if applicable)

Agents are used within workflows defined in `src/byte/workflow/workflows/`. To wire the new agent into a workflow:

```python
# In a workflow file (e.g., src/byte/workflow/workflows/my_workflow.py):
from byte.node.agents import MyNewAgentNode

class MyWorkflow(BaseWorkflow):
    def build(self, graph):
        graph.add_node(MyNewAgentNode, goto=EndNode)
```

The `goto` parameter in `add_node` is passed to the agent's `boot()` method and determines which node the agent routes to after completing its work.

---

## Naming Conventions

| Item                  | Convention                                | Example                |
| --------------------- | ----------------------------------------- | ---------------------- |
| File name             | `<name>_agent_node.py`                    | `review_agent_node.py` |
| Class name            | `<Name>AgentNode`                         | `ReviewAgentNode`      |
| Message class         | `<Name>AgentMessage`                      | `ReviewAgentMessage`   |
| `agent_name` field    | Human-readable title                      | `"Review Agent"`       |
| Container name (auto) | `<name>_agent_node` (snake_case of class) | `review_agent_node`    |

---

## Quick Reference: Files to Touch

When creating a new agent, you will modify/create these files:

1. **CREATE** `src/byte/node/agents/<name>_agent_node.py` — The agent implementation
2. **EDIT** `src/byte/node/messages.py` — Add message type to `ByteAIMessage`
3. **EDIT** `src/byte/node/agents/__init__.py` — Add exports and dynamic import
4. **EDIT** `src/byte/node/service_provider.py` — Add to `agents()` list
5. **CREATE/EDIT** `src/byte/workflow/workflows/<workflow>.py` — Wire into a workflow (if applicable)
