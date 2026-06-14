# Architecture Overview

**Category**: Explanation

Byte's architecture is built around a command-driven workflow engine that coordinates multiple agents, phases, and tools into a cohesive system. This page explains how the pieces fit together and why this design enables safe, controllable AI-assisted development.

## Core Concept: Commands Drive Workflows

When you execute a slash command (e.g., `/coder`), you're invoking a `Command`. Commands are lightweight entry points that wire up a workflow and delegate execution to it. The workflow orchestrates everything that follows.

```mermaid
graph TD
    A["User runs /coder<br/>implement feature X"]
    B["CoderCommand.execute()"]
    C["CoderWorkflow<br/>manages phases and state"]
    D["Agent Graph<br/>LangGraph StateGraph"]

    A --> B
    B --> C
    C --> D
```

This separation of concerns means commands remain simple and focused—they don't contain business logic themselves. They simply prepare the request and hand it off to the workflow engine.

## Workflows: Multi-Phase Orchestration

A workflow defines a sequence of **phases** that must be completed in order. Each phase has:

- A **description** of what needs to happen
- A list of **tools** available to complete it
- An **Agent Node** that executes the phase
- A **status** (pending, in_progress, completed, or blocked)

Phases are not arbitrary steps—they represent distinct stages of work. For example, the `CoderWorkflow` defines:

1. **select-skills-and-files** — Prepare the context and instruction
2. **create-plan** — Design the implementation
3. **apply-changes** — Write the code
4. **linting** — Validate and fix lint errors
5. **summary** — Recap what was done

An agent works through phases sequentially. The workflow tracks phase progress automatically—every tool call in a phase receives `phase_id` and `phase_status` arguments injected by the orchestration layer, enabling any tool to report phase completion. The agent simply calls tools to make progress; phase status flows through every tool invocation.

## Agent Nodes: The Workers

An **Agent Node** is a LangGraph node that runs an LLM-powered agent. It receives the workflow state, looks at the current pending phase, and uses available tools to make progress. Key characteristics:

- **One LLM invocation per agent** — The node prompts the agent and waits for a response
- **Tool-driven** — The agent doesn't compute; it calls tools (file edits, linting, etc.)
- **Phase-aware** — The agent sees which phase is pending and focuses only on that
- **Stateless loop** — The node can be called repeatedly; state is managed by the workflow

Different Agent Nodes can specialize in different tasks. `Coder Agent` is optimized for code generation; other domains might have specialized agents for their own workflows.

**Routing Node is not an agent.** Unlike Agent Nodes, `Routing Node` extends `Base Node`, not `Base Agent Node`. It contains no LLM invocation and makes routing decisions based purely on workflow state and phase status. It's a deterministic switch statement, not a reasoning engine.

## Harness Agent: Context Preparation

Before domain-specific agents execute, **Harness Agent** runs as the start node for every workflow except `ask`. Its single, critical job: analyze the user's request and conversation history, then prepare a scoped instruction for the downstream agent.

**What it does:**

Harness Agent acts as a **harness selector**. It examines the user's intent, identifies which skills are relevant, determines which files need editing, gathers reference materials, and synthesizes a clear, actionable instruction. It uses a `reasoning` tier LLM for this context-preparation work—a relatively expensive step, but essential for precision.

**The separation that matters:**

The downstream agent (e.g., `Coder Agent`, `Documentation Agent`) receives **no access to conversation history**. It only sees what Harness Agent has prepared: the skills list, editable files, reference materials, and the synthesized instruction. This is deliberate. It creates a clean boundary:

- **Harness Agent** — Owns context selection, scoping, and instruction synthesis
- **Domain Agent** — Owns execution against the prepared scope

This separation prevents agents from being distracted by historical context and ensures they stay focused on the current task.

**In the code:**

Every workflow starts the same way:

```python
graph = GraphBuilder(start_node=HarnessAgentNode)
```

And the first phase always runs via Harness Agent:

```python
PhaseModel(
    id="select-skills-and-files",
    executed_by=HarnessAgentNode,
    tools=[BootstrapAgentTool, UserInputTextTool, UserConfirmTool, UserSelectTool],
)
```

Harness Agent uses `BootstrapAgentTool` to package everything it discovered into a coherent bootstrap instruction that seeds the domain agent's first invocation. The downstream agent then operates entirely from that bootstrap—no conversation history, no context drift.

## Tools: The Hands of the Agent

Tools are the **concrete operations** that agents invoke. They fall into two categories:

### Workflow Tools

- `CreatePlanTool` — Plan out the implementation steps
- `CompleteTurnTool` — Finish the workflow with a summary

### Domain-Specific Tools

- `EditFileTool`, `WriteFileTool`, `DeleteFileTool` — Modify files
- `LintTool` — Validate code
- `UserInputTool`, `UserSelectTool` — Ask the user for input

Tools have strict input schemas (JSON Schema), so the agent's requests are validated before execution. Tool results feed back into the agent's next message, creating a feedback loop.

## The Graph: LangGraph StateGraph

Under the hood, workflows are compiled into a **LangGraph StateGraph**—a directed graph of nodes and edges that orchestrates execution. The `GraphBuilder` creates this graph:

```mermaid
graph TD
    START["START"]
    start_node["start_node<br/>(Harness Agent)"]
    coder_agent_node["coder_agent_node<br/>(Coder Agent)"]
    tool_node["tool_node<br/>(Tool Node — routes tool calls)"]
    routing_node["routing_node<br/>(Routing Node — determines next step)"]
    END["END"]

    START --> start_node
    start_node --> coder_agent_node
    coder_agent_node --> tool_node
    tool_node --> routing_node
    routing_node --> END
```

**Why this structure?**

- **Separation of concerns** — Tool invocation is handled by `ToolNode`, not the agent
- **Controllable loops** — The routing node decides whether to loop back to the agent or move forward
- **Persistent state** — LangGraph's checkpointer saves state after every step, enabling resumable workflows
- **Streaming** — Events flow through the graph and surface in the TUI in real time

## State: Single Source of Truth

The `BaseState` TypedDict holds everything:

- **workflow_phases** — All phases and their current statuses
- **harness** — Skills, editable files, and instruction for the agent
- **history_messages** — Persistent conversation history
- **scratch_messages** — Ephemeral validation or error messages
- **touched_files** — Files modified during this workflow
- **user_request** — The original request that kicked off the workflow
- **metadata** — Analytics and tracking info

When a tool executes (e.g., a file edit), it updates the relevant part of state. The next agent invocation sees the updated state, so it knows what changed.

## Routing: Deciding What Comes Next

The `Routing Node` is **not an agent**—it's a deterministic router. It extends `Base Node`, not `Base Agent Node`, and contains no LLM invocation. It's pure conditional state logic.

After each agent response, Routing Node checks the workflow state:

1. **Checks for cancellation** — If the cancel event is set, routes to `end_node` immediately
2. **Checks if workflow is in an agent phase** — Calls `PhaseUtils.is_workflow_agent(state)` to determine if the current phase requires agent execution
3. **Routes to pending phase's executor** — If a phase is pending, looks up its `executed_by` target and routes there
4. **Falls back to routing state** — Otherwise uses the routing state's `target` to determine the next node

This routing logic keeps workflows moving forward based purely on phase status and state conditions—no LLM, no reasoning, no autonomy. It's a switch statement.

## Why This Architecture?

**Safety through control** — Agents don't autonomously loop forever. Phases provide explicit boundaries, and the user always has visibility into what's happening.

**Reusability** — New workflows inherit the same graph structure, phase model, and state management. You define phases and tools; the engine handles orchestration.

**Observability** — Every step (agent invocation, tool call, phase update) is a node in the graph. The TUI streams events in real time, and the checkpointer logs every state change.

**Extensibility** — New domains add custom agent nodes and tools without touching the core graph. Tools and phases compose cleanly because they all speak the same StateGraph language.

## Architecture Diagram

```mermaid
graph TD
    User["👤 User Executes /coder"]
    Cmd["📍 CoderCommand"]
    WF["🔄 CoderWorkflow<br/>(defines phases)"]
    GB["🏗️ GraphBuilder<br/>(compiles to LangGraph)"]
    Graph["📊 StateGraph<br/>(LangGraph)"]

    HarnessPhase["📋 Phase 1: select-skills-and-files<br/>(context preparation)"]
    HarnessNode["🧠 Harness Agent<br/>(context selector)"]
    BootstrapTool["🔌 BootstrapAgentTool<br/>(package instruction,<br/>skills, files)"]
    Bootstrap["📦 Bootstrap Output<br/>(no conversation history<br/>seen by domain agent)"]

    DomainPhases["📋 Phases 2+<br/>create-plan<br/>apply-changes<br/>linting<br/>summary"]
    Agent["🤖 Domain Agent<br/>(Coder Agent,<br/>Documentation Agent, etc)"]
    Tools["🔧 Tool Node<br/>(routes tool calls)"]
    Tool1["EditFileTool<br/>WriteFileTool<br/>LintTool<br/>etc<br/>(phase_id & phase_status<br/>injected automatically)"]
    Router["🔀 Routing Node<br/>(decide next step)"]
    End["⏹️ End Node"]

    User -->|invokes| Cmd
    Cmd -->|prepares request| WF
    WF -->|provides phases| GB
    GB -->|builds| Graph

    Graph -->|execution starts| HarnessNode
    HarnessNode -->|Phase 1| HarnessPhase
    HarnessPhase -->|analyze user request<br/>& conversation history| HarnessNode
    HarnessNode -->|invoke| BootstrapTool
    BootstrapTool -->|identifies skills,<br/>editable files,<br/>reference materials| Bootstrap

    Bootstrap -->|seeds domain agent<br/>scoped instruction only| Agent
    Agent -->|Phase 2+| DomainPhases
    Agent -->|invoke tools| Tools
    Tools -->|execute| Tool1
    Tool1 -->|update state<br/>& phase status| Graph
    Tools -->|return result| Agent

    Agent -->|done with response| Router
    Router -->|more phases pending| Agent
    Router -->|all complete| End
    Router -->|phase blocked| End

```

## Key Takeaways

1. **Commands are entry points** — they hand off to workflows, not business logic containers
2. **Workflows define phases** — a sequence of distinct, bounded work units
3. **Agents are phase executors** — they see one pending phase and use available tools
4. **Tools are the operations** — agents call tools; tools update state
5. **Routing Node drives flow** — it decides whether to loop, advance, or finish
6. **StateGraph is the engine** — LangGraph orchestrates all of this persistently and observably

This design prioritizes **clarity, control, and composability** over speed or autonomy. Every workflow is understandable, observable, and can be extended without modifying core infrastructure.
