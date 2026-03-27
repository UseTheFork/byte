# Design: Agent Domain — Python to Node/TS Migration

**Date:** 2026-03-26
**Branch:** dev-v3-node
**Scope:** Full migration of the Python `byte/agent` domain to TypeScript/Node, plus two new self-contained domains (`llm`, `memory`) and a new `workflows` top-level domain. Python source is preserved as the reference implementation.

---

## Overview

The Python agent domain (`byte/agent/`) is migrated to TypeScript under an expanded `graphs/` domain, with `workflows/` as a new top-level domain. The key architectural changes are:

1. `implementations/` is renamed to `agents/` — agent classes extend `Node` (not a separate `Agent` base that runs graphs itself)
2. Agents compile subgraphs but do not execute themselves — execution is owned by `Workflow`
3. All routing goes through a `RoutingNode` that reads `going_to`/`coming_from` from state — no `Command(goto=...)` pattern
4. `workflows/` composes agents as LangGraph subgraph nodes into sequential pipelines
5. `AgentService` dispatches to a `Workflow`, not directly to an agent

---

## New Packages

Already installed via LangGraph dependency. No additions required.

---

## Repository Layout

```
node/src/
  llm/
    service/llm-service.ts
    service-provider.ts
    index.ts

  memory/
    service/memory-service.ts
    service-provider.ts
    index.ts

  graphs/
    state.ts                      ← update: add going_to, coming_from
    schemas.ts                    ← existing, unchanged
    nodes/
      base-node.ts                ← abstract Node class
      assistant-node.ts
      start-node.ts
      end-node.ts
      tool-node.ts
      routing-node.ts             ← new
      dummy-node.ts
      lint-node.ts                ← stub
      parse-blocks-node.ts        ← stub
      validation-node.ts          ← stub
      extract-node.ts             ← stub
    agents/
      base.ts                     ← abstract Agent extends Node
      coder/agent.ts + prompt.ts
      ask/agent.ts + prompt.ts
      research/agent.ts + prompt.ts
      cleaner/agent.ts + prompt.ts
      commit/agent.ts + prompt.ts
      convention/agent.ts + prompt.ts
    utils/
      graph-builder.ts
    service-provider.ts           ← AgentServiceProvider (already started)
    index.ts

  workflows/
    base.ts                       ← abstract Workflow
    ask/workflow.ts               ← AskWorkflow
    utils/workflow-builder.ts
    service/agent-service.ts
    service-provider.ts
    index.ts

  main.ts                         ← wire all new providers
```

**Modified files:**
- `node/src/graphs/state.ts` — add routing fields
- `node/src/graphs/service-provider.ts` — register nodes and agents
- `node/src/main.ts` — add LLMServiceProvider, MemoryServiceProvider, AgentServiceProvider, WorkflowServiceProvider

---

## Architecture

### LLM Domain (`llm/`)

Provides LangChain model instances. No external state — reads model names from config on `boot()`.

```typescript
class LLMService extends Service {
  static token = Symbol('LLMService')

  getMainModel(): BaseChatModel   // ChatAnthropic using config.llm.main_model
  getWeakModel(): BaseChatModel   // ChatAnthropic using config.llm.weak_model
}
```

`LLMServiceProvider` registers `LLMService` as a singleton.

---

### Memory Domain (`memory/`)

Provides LangGraph checkpointers and thread ID management.

```typescript
class MemoryService extends Service {
  static token = Symbol('MemoryService')

  getOrCreateThread(): string         // returns existing or new UUID thread ID
  getSaver(): BaseCheckpointSaver     // returns MemorySaver (in-memory)
}
```

Thread IDs are stored in a per-session in-memory map. `MemoryServiceProvider` registers `MemoryService` as a singleton.

---

### State Update (`graphs/state.ts`)

Two new fields added to `BaseStateSchema`:

```typescript
going_to: z.string().nullable().default(null),
coming_from: z.string().nullable().default(null),
```

`going_to` — the next node/agent the `RoutingNode` should route to. Set by any node before it returns.
`coming_from` — the node that just ran. Set by each node to its own name before returning, so downstream nodes have routing context. The `RoutingNode` never modifies this field.

All existing fields are unchanged.

---

### Base Node (`graphs/nodes/base-node.ts`)

```typescript
export abstract class Node extends Service {
  abstract call(
    state: BaseState,
    config?: RunnableConfig,
  ): Promise<Partial<BaseState>>
}
```

Extends `Service` (which extends `Bootable`), giving every node `app`, `boot()`, and `emit()`. The `call()` signature matches the LangGraph JS node convention — instances can be passed directly to `graph.addNode()`.

---

### Foundational Nodes

| Node | Behaviour |
|---|---|
| `StartNode` | Clears scratch messages, resets metadata, sets `going_to: 'assistant_node'` |
| `AssistantNode` | Reads `AssistantContext` from `config.configurable.assistant`, invokes LLM. Sets `going_to: 'tool_node'` if tool calls present, else `going_to: 'end_node'` |
| `ToolNode` | Executes tool calls from last scratch message, appends `ToolMessage` results to scratch, sets `going_to: 'assistant_node'` |
| `EndNode` | Promotes scratch messages to history wrapped in boundaries, sets `going_to: '__end__'` |
| `RoutingNode` | Reads `going_to` from state, emits a routing event (for observability), returns state unchanged. Conditional edge performs the actual routing: `(state) => state.going_to` |
| `DummyNode` | No-op placeholder, sets `going_to: '__end__'` |

**Stubbed nodes** (`LintNode`, `ParseBlocksNode`, `ValidationNode`, `ExtractNode`) — no-ops that set `going_to: '__end__'`. Pending migration of `code_operations`, `lint`, and `clipboard` domains.

---

### AssistantContext via config

Python passes context via `Runtime[AssistantContextSchema]`. In LangGraph JS this is passed through `config.configurable.assistant`. Nodes read it as:

```typescript
const context = config?.configurable?.assistant as AssistantContext
```

The `GraphBuilder` sets this on `compile()`:

```typescript
graph.build().compile({
  checkpointer,
  configurable: { assistant: await agent.getAssistantContext() },
})
```

---

### GraphBuilder (`graphs/utils/graph-builder.ts`)

```typescript
class GraphBuilder {
  constructor(app: IApplication, startNode: typeof Node = AssistantNode)

  addNode<T extends Node>(nodeClass: new(app) => T, options?: Record<string, unknown>): T
  build(): StateGraph<typeof BaseStateSchema>
}
```

- Auto-adds `StartNode`, `EndNode`, `RoutingNode`, `DummyNode` on construction
- `build()` creates `StateGraph(BaseStateSchema)`, registers all nodes, wires all edges through `routing_node` via a single conditional edge: `(state) => state.going_to`
- Entry point: `start_node`
- Finish point: `__end__` (reached when `going_to === '__end__'`)

---

### Agent Base (`graphs/agents/base.ts`)

```typescript
export abstract class Agent extends Node {
  private _compiled: CompiledStateGraph | null = null

  abstract getPrompt(): ChatPromptTemplate
  abstract getUserTemplate(): string[]
  getEnforcement(): string[] { return [] }
  getTools(): StructuredTool[] { return [] }

  abstract build(): Promise<CompiledStateGraph>

  async compile(): Promise<CompiledStateGraph> {
    if (this._compiled === null) {
      this._compiled = await this.build()
    }
    return this._compiled
  }

  // Satisfies Node.call() — invoked when workflow uses agent as a subgraph node
  async call(state: BaseState, config?: RunnableConfig): Promise<Partial<BaseState>> {
    const graph = await this.compile()
    return graph.invoke(state, config)
  }

  async getAssistantContext(): Promise<AssistantContext> {
    const llm = this.app.make(LLMService)
    return {
      mode: 'main',
      prompt: this.getPrompt(),
      user_template: this.getUserTemplate(),
      main: llm.getMainModel(),
      weak: llm.getWeakModel(),
      enforcement: this.getEnforcement(),
      agent: this.constructor.name,
      tools: this.getTools(),
    }
  }
}
```

Agents do not implement `execute()`. Execution is owned entirely by `Workflow`.

---

### Agent Implementations

Six agents: `CoderAgent`, `AskAgent`, `ResearchAgent`, `CleanerAgent`, `CommitAgent`, `ConventionAgent`. Each extends `Agent` and implements `getPrompt()`, `getUserTemplate()`, and `build()`.

Example — `AskAgent`:

```typescript
class AskAgent extends Agent {
  getPrompt() { return askPrompt }
  getUserTemplate() { return askUserTemplate }
  getTools() { return [loadConvention, gitGrep] }

  async build(): Promise<CompiledStateGraph> {
    const graph = new GraphBuilder(this.app)
    graph.addNode(AssistantNode)
    graph.addNode(ToolNode)
    const checkpointer = this.app.make(MemoryService).getSaver()
    return graph.build().compile({
      checkpointer,
      configurable: { assistant: await this.getAssistantContext() },
    })
  }
}
```

Prompts are ported from Python as tagged template literals in co-located `prompt.ts` files.

`AgentServiceProvider` registers all agents as singletons. No commands are registered here.

---

### Workflow Base (`workflows/base.ts`)

```typescript
export abstract class Workflow extends Service {
  abstract build(): Promise<CompiledStateGraph>
  protected abstract getEntryAgent(): string

  async execute(request: string, threadId?: string): Promise<void> {
    const memory = this.app.make(MemoryService)
    const thread = threadId ?? memory.getOrCreateThread()
    const graph = await this.build()

    await graph.invoke(
      { user_request: request, going_to: this.getEntryAgent() },
      { configurable: { thread_id: thread } },
    )
  }
}
```

---

### WorkflowBuilder (`workflows/utils/workflow-builder.ts`)

```typescript
class WorkflowBuilder {
  constructor(app: IApplication)

  addAgent(agentClass: new(app) => Agent): void
  build(): StateGraph<typeof BaseStateSchema>
}
```

- Creates a top-level `StateGraph(BaseStateSchema)`
- Adds `RoutingNode`
- For each agent: resolves instance via `app.make(agentClass)`, calls `agent.compile()`, adds compiled subgraph as a node keyed by snake_case class name (`CoderAgent` → `'coder_agent'`)
- Wires single conditional edge from `routing_node`: `(state) => state.going_to`
- Entry point: `routing_node`

---

### AskWorkflow (`workflows/ask/workflow.ts`)

```typescript
class AskWorkflow extends Workflow {
  protected getEntryAgent() { return 'ask_agent' }

  async build(): Promise<CompiledStateGraph> {
    const graph = new WorkflowBuilder(this.app)
    graph.addAgent(AskAgent)
    return graph.build().compile({
      checkpointer: this.app.make(MemoryService).getSaver(),
    })
  }
}
```

Execution flow: `routing_node → ask_agent (subgraph) → routing_node → __end__`

After the `AskAgent` subgraph completes, its `EndNode` sets `going_to: '__end__'`. Control returns to the parent workflow's `routing_node`, which routes to `__end__`.

---

### AgentService (`workflows/service/agent-service.ts`)

```typescript
class AgentService extends Service {
  static token = Symbol('AgentService')

  private _currentWorkflow: new(app: IApplication) => Workflow = AskWorkflow

  async execute(request: string): Promise<void> {
    const workflow = this.app.make(this._currentWorkflow)
    return workflow.execute(request)
  }

  setActiveWorkflow(workflowClass: new(app: IApplication) => Workflow): void {
    this._currentWorkflow = workflowClass
  }
}
```

`WorkflowServiceProvider` registers `AgentService`, `AskWorkflow`, and all future workflow classes as singletons.

---

### Service Wiring (`main.ts`)

Providers added in dependency order:

```typescript
app.bootstrapWith([
  // ... existing providers (Foundation, CLI, Config, Git, Files) ...
  LLMServiceProvider,         // no dependencies
  MemoryServiceProvider,      // no dependencies
  AgentServiceProvider,       // depends on LLM, Memory
  WorkflowServiceProvider,    // depends on agents
])
```

---

## Out of Scope

- `LintNode` full implementation — depends on `lint` domain (not yet migrated)
- `ParseBlocksNode` full implementation — depends on `code_operations` domain (not yet migrated)
- `ValidationNode` full implementation — depends on validator infrastructure
- `ExtractNode` full implementation — depends on `clipboard` domain (not yet migrated)
- `AICommentWatcherService` full implementation — depends on `AskAgent` being wired to file events
- `readFiles` tool full implementation — depends on tools system
- Commands (`AskCommand`, `ResearchCommand`, `ConfigAgentCommand`) — migrated separately
- `CoderWorkflow`, `ResearchWorkflow`, etc. — only `AskWorkflow` in this spec
