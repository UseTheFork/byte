# File Watching & AI Comments

Byte automatically watches files in your project for changes. When it detects special AI comment
markers, it can automatically add files to context and trigger actions.

## AI Comment Markers

Byte recognizes four types of AI comment markers, each triggering different behavior:

### Editable marker (`AI:`)

Used for standard code modification requests. Files are added to context as **editable**, allowing
the AI to propose SEARCH/REPLACE blocks.

Marker Quick Reference:

AI: - Request code modifications (editable mode)
AI @ - Provide reference context (read-only mode)
AI ? - Ask questions about code (read-only mode, no changes)
AI ! - Mark urgent/critical issues (editable mode, highest priority)
Read-only marker (AI@)

Used to provide reference context without allowing modifications. Files are added as read-only.

# AI@ Reference this pattern for other implementations

class BaseHandler:
 def handle(self):
 pass

Behavior:

• File added to context in read-only mode
 • AI can reference the code but cannot propose changes
 • Useful for providing examples or patterns to follow

─────────────────────────────────────────────────────────────────────────────────────────────────────
Question marker (AI?)

Used to ask questions about code. The AI provides answers and recommendations without making changes.

Before (problematic code):

# AI? Should this use a context manager instead?

file = open("data.txt")
data = file.read()
file.close()

Behavior:

• File added to context in read-only mode
 • AI analyzes the code and provides recommendations
 • No code changes are proposed
 • Response includes best practices and alternatives

Example AI Response:

Yes, this should definitely use a context manager. The current code has several issues:

1. If an exception occurs between open() and close(), the file remains open
2. Manual resource management is error-prone
3. Not following Python best practices


Recommended approach:

````python
# Improved version using context manager
with open("data.txt") as file:
    data = file.read()
# File automatically closed when exiting the with block


Benefits:

 • Automatic cleanup even if exceptions occur
 • More Pythonic and readable
 • Follows RAII pattern and prevents resource leaks



---

### Urgent task marker (`AI!`)

Used for critical issues requiring immediate attention. Takes priority over other markers.

```python
# AI! Fix this security vulnerability immediately
password = request.args.get('password')  # Plain text password in GET request!


Behavior:

 • File added to context in editable mode
 • Takes highest priority if multiple AI comments exist
 • AI proposes immediate fixes using SEARCH/REPLACE blocks
 • Clear indication this is a critical issue

─────────────────────────────────────────────────────────────────────────────────────────────────────

How It Works

Detection Flow

 1 File change detected: Byte's watcher service detects when you save a file
 2 AI comment scan: File content is scanned for AI:, AI@, AI?, or AI! markers
 3 Auto-add to context: File is automatically added with appropriate mode:
    • AI: or AI! → Editable mode
    • AI@ or AI? → Read-only mode
 4 Prompt interruption: Current prompt is interrupted to process the AI comment
 5 AI response: AI processes the comment based on marker type:
    • : or ! → Proposes code changes (CoderAgent)
    • ? → Provides analysis and answers (AskAgent)
    • @ → References the code as context

Workflow steps:

1. You add an AI comment in your editor
2. Save the file
3. Byte automatically:
   - Detects the AI comment marker
   - Adds the file to context (editable for `AI:` and `AI!`, read-only for `AI@`)
   - Interrupts the current prompt
   - Shows you the AI comment
   - Asks the AI to implement the requested changes
4. AI responds with SEARCH/REPLACE blocks showing proposed changes
5. You review and approve or reject the changes
6. If approved, changes are applied and linters run automatically (if enabled)

**Multiple comments:**

If multiple AI comments are detected, they're processed together based on priority:

1. `AI!` (urgent) takes precedence
2. Then `AI?` (questions)
3. Then `AI:` (regular tasks)
````
