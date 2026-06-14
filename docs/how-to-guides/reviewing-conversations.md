# Review Recorded Conversations

**Category**: How-to Guide

Byte records every LLM interaction to your local cache. Each recorded conversation is a snapshot of the exact prompt sent to the model — system messages, constitution, injected context, user instructions, and all tool calls. This gives you full visibility into how Byte reasons through tasks. Use recordings to debug prompt design, verify that the constitution is being applied correctly, inspect what context was available to the model, and understand how the system reached specific decisions.

## Prerequisites

- Byte installed on your system
- At least one completed workflow run
- Basic familiarity with Byte's workflow system

## Step 1: Understand the Cache Structure

Byte stores recorded conversations at `.byte/cache/conversations/{workflow_name}/{step}_{node}.md` in your project root.

- **workflow_name**: The name of the workflow that ran (e.g., `documentation-workflow`, `code-review`)
- **step**: The execution step number within the workflow (e.g., `0`, `1`, `2`)
- **node**: The name of the agent node that processed the step (e.g., `assistant_node`, `tool_node`)

Example path: `.byte/cache/conversations/documentation-workflow/1_assistant_node.md`

Each file contains the complete prompt history for a single agent invocation — everything the LLM received before generating its response.

## Step 2: Open a Recorded Conversation

Navigate to `.byte/cache/conversations/` in your project and open any `.md` file:

```bash
# List all recorded conversations
ls .byte/cache/conversations/

# Open a specific conversation
cat .byte/cache/conversations/my-workflow/0_assistant_node.md
```

The file is plain markdown, readable in any text editor or terminal. Each section is separated by a clear header:

```
======== SystemMessage ========
[system message content]

======== HumanMessage ========
[user message content]

======== AIMessage ========
[model response]
```

## Step 3: Interpret Message Types

A recorded conversation contains several message types. Each represents a distinct part of the prompt sent to the LLM.

### SystemMessage

The system message sets the LLM's role, behavior, and constraints. This includes:

- Byte's core system prompt defining its identity as a CLI agent
- Your project's constitution (all governance principles and standards)
- Behavioral guidelines for the specific workflow
- Instructions on how to structure responses

If you suspect the constitution isn't being applied, check the SystemMessage section first.

### HumanMessage

The human message contains the actual task or request. This includes:

- The user's original instruction or query
- Task-specific guidance and context
- Details about files being edited, created, or referenced
- Workflow metadata and phase information

### AIMessage

The AI message is the model's response. It contains:

- Reasoning or explanation of the approach
- Tool calls made by the model (structured JSON with tool names and arguments)
- Any follow-up decisions or status updates

If tool calls are present, they appear formatted as:

```
Tool Calls:
  - tool_name: {"arg1": "value1", "arg2": "value2"}
  - another_tool: {"param": "data"}
```

### Other Message Types

Depending on the workflow, you may see:

- **ToolMessage**: Results returned from executed tools (e.g., file contents, command output)
- **ToolErrorMessage**: Errors encountered during tool execution
- **MessageHistory**: Previous conversation turns (when multi-turn interactions are involved)

## Step 4: Read Through a Conversation

Open a conversation file and scan for what you need to verify:

### Find the Constitution Injection

In the SystemMessage, look for the constitution principles. Search for headers like:

```
## Core Principles
```

This confirms that governance rules were injected into the prompt. If the constitution is missing or incomplete, that explains why the model didn't follow expected constraints.

### Find the Injected Context

In the HumanMessage, look for section tags like:

```
<session_context type="file" key="...">
[file or web content here]
</session_context>
```

These sections show what external context the model had access to. If you added files via `/context` but don't see them here, context injection failed.

### Review Tool Calls

In the AIMessage, the Tool Calls section shows exactly what the model attempted to do. Check:

- Are tool names correct and spelled right?
- Do argument values make sense for the task?
- Are file paths correct?
- Did the model use the right tools in the right order?

If a tool call looks wrong, you've found where the model went off track.

### Trace Workflow Decisions

For multi-step workflows, open the files in sequence (0_assistant_node.md, then 1_assistant_node.md, etc.). Each file shows what the model knew at that step and what decisions it made. This traces the exact path the workflow took.

## Common Use Cases

### Debugging an Unexpected Tool Call

The model called the wrong tool or passed incorrect arguments. Open the conversation file and check:

1. What was in the HumanMessage? Was the task clear?
2. What was in the SystemMessage? Were tool descriptions correct?
3. What tool calls appear in the AIMessage? What went wrong?

Example: If the model tried to edit a file that doesn't exist, check whether the file path in HumanMessage was correct and whether the model's understanding of the project structure (from SystemMessage) was accurate.

### Verifying Constitution Enforcement

You want to confirm that your project's governance principles are being applied. Check:

1. Open the SystemMessage section
2. Search for your constitution principles by name or ID (e.g., "domain-driven-design", "strict-typing")
3. Verify they appear in full and are readable

If they're missing or truncated, the model may not have been constrained by them.

### Inspecting Context Injection

You added files via `/context` and want to confirm the model received them:

1. Open the HumanMessage section
2. Search for `<session_context>`
3. Verify that your files appear with correct keys
4. Check that file content is present (not just file names)

If files are missing, re-add them with `/context` and run the workflow again.

### Checking Tool Execution Order

Multi-step workflows use tool nodes to execute actions. If the workflow took an unexpected path:

1. Open the first assistant_node file (step 0)
2. Check what tool it called and with what arguments
3. Open the corresponding tool_node file (step 0_tool_node)
4. See what result was returned
5. Open the next assistant_node file (step 1)
6. Check whether the model's next action made sense given the previous result

This traces cause-and-effect through the workflow.

### Analyzing Prompt Size and Structure

Open a conversation file and visually scan its size:

- **Small files** (~1-5 KB): Minimal context, simple task
- **Medium files** (~10-50 KB): Normal complexity with some context
- **Large files** (>100 KB): Heavy context, large codebase, or accumulated message history

If files are growing very large, context may be bloating. This can reduce model quality and increase cost. Consider clearing session context or breaking workflows into smaller pieces.

## Understanding Cache Lifecycle

The conversation cache is cleared at the start of every workflow run. When you run a new workflow:

1. Byte deletes all previous conversations for that workflow (from `.byte/cache/conversations/{workflow_name}/`)
2. New conversations are recorded as the workflow executes
3. When the workflow ends, files remain on disk for review

**Important**: Conversations are only kept for the most recent run of each workflow. If you run the same workflow twice, the first run's recordings are deleted.

To preserve conversations for long-term analysis, copy them to another directory before running the workflow again:

```bash
# Save conversations before re-running
cp -r .byte/cache/conversations/my-workflow ~/my-workflow-archive/run-1
```

## Tips for Effective Review

- **Start from the end and work backward**: Open the final step first to see what the model concluded, then trace back through earlier steps to understand how it got there.
- **Compare multiple runs**: Run the same workflow twice with different inputs or context and compare their conversation files side-by-side.
- **Search for keywords**: Use `grep` to search all conversations for specific terms: `grep -r "constitution" .byte/cache/conversations/`
- **Monitor token usage**: Conversation files don't show token counts directly, but the TUI output during workflow execution does. Combine that with conversation review to understand cost drivers.

## Next Steps

Now that you can review conversations, explore how to use this information to:

- Refine prompts and system messages in your workflows
- Debug tool integrations and verify correct execution
- Optimize context injection for better model performance
- Understand the constitution application in real workflows

For deeper insights into how Byte assembles prompts and manages state, see the explanation section on workflow execution and prompt assembly.
