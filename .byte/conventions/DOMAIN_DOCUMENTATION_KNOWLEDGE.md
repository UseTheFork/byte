---
name: knowledge-domain
description: Domain documentation for src/byte/knowledge - session context management, web scraping, and runtime knowledge storage. Use when working with session context, web content extraction, or understanding how runtime knowledge is managed and injected into AI prompts.
---

# Knowledge Domain Documentation

## Domain Purpose

Manages **runtime session context** - temporary knowledge that persists within a single Byte session but doesn't belong in permanent conventions. Handles web content scraping, file-based context injection, and display of active context to users.

**Key Distinction**: `knowledge` = session-scoped runtime context; `conventions` = project-scoped persistent patterns.

## Core Responsibilities

- Store and retrieve session-specific documentation/context
- Scrape web pages and convert to markdown for AI consumption
- Inject session context into AI prompts via event hooks
- Display active context items to users in CLI
- Manage file-based persistence in `.byte/session_context/`

## Key Components

### SessionContextModel

File-backed model for individual context items. Content stored in `.byte/session_context/{slugified-key}.md`.

```python
# Create and persist context
model = app.make(SessionContextModel,
    type="web",  # "web" | "file" | "agent"
    key="api-docs",
    content="# API Documentation\n..."
)

# Lazy-load content from disk
text = model.content  # Reads from file

# Update content
model.set_content("Updated content")

# Cleanup
model.delete()  # Removes file from disk
```

**Pattern**: Similar to FileContext - lazy content loading, automatic file management.

### SessionContextService

Central service managing all session context via `ArrayStore`. Hooks into event system to inject context into prompts.

```python
service = app.make(SessionContextService)

# Add context (stores model in ArrayStore)
service.add_context(model)

# Retrieve specific item
model = service.get_context("api-docs")

# Get all context
all_items = service.get_all_context()  # dict[str, SessionContextModel]

# Remove item (deletes file + removes from store)
service.remove_context("api-docs")

# Clear all
service.clear_context()
```

**Event Hook**: `add_session_context_hook` listens to `GATHER_PROJECT_CONTEXT` event, formats all context items with XML boundaries, and injects into `session_docs` payload list.

### CLIContextDisplayService

Displays active session context and conventions in CLI before each prompt.

```python
# Hooked to PRE_PROMPT_TOOLKIT event
# Renders two-column panel:
# [Session Context] | [Conventions]
# - api-docs        | - code-patterns
# - style-guide     | - api-design
```

## Commands

### `/web <url>`

Scrapes webpage using headless Chrome, converts to markdown, displays preview, prompts to add to context.

```python
# Flow:
# 1. ChromiumService.do_scrape(url) -> markdown
# 2. Display markdown preview in panel
# 3. Prompt: "Add to context?" [Yes/Clean with LLM/No]
# 4. If "Clean with LLM": CleanerAgent extracts relevant info
# 5. Store as SessionContextModel with slugified URL as key
```

**Integration**: Depends on `web` domain (ChromiumService), `agent` domain (CleanerAgent).

### `/ctx:file <path>`

Reads file from disk, adds to session context with YAML frontmatter.

```python
# Adds YAML header:
# ---
# file_path: src/example.py
# ---
#
# [file contents]
```

**Path Resolution**: Relative paths resolved from project root (`app["path"]`).

### `/ctx:ls`

Lists all session context keys in formatted panel.

### `/ctx:drop <key>`

Removes context item by key. Provides tab-completion of existing keys.

```python
async def get_completions(self, text: str) -> List[str]:
    # Returns keys matching input prefix
    return [key for key in context_items.keys() if key.startswith(text)]
```

## Data Models

### SessionContextModel Fields

```python
type: Literal["web", "file", "agent"]  # Source of context
key: str                                # Unique identifier
file_path: Path                         # .byte/session_context/{slug}.md
content: str                            # Lazy-loaded from file
```

### Context Injection Format

```xml
<session_context type="web" key="api-docs">
# API Documentation
...
</session_context>
```

Uses `Boundary.open(BoundaryType.SESSION_CONTEXT, meta={...})` for consistent XML formatting.

## Business Logic Patterns

### File-Based Persistence

**Why**: Session context can be large (web pages, documentation). Storing in memory wastes resources. File-based storage enables:

- Lazy loading (only read when needed)
- Persistence across command executions within session
- Easy cleanup (delete files on clear)

```python
# Pattern: Property-based lazy loading
@property
def content(self) -> str:
    try:
        return self.file_path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return ""  # Graceful degradation
```

### ArrayStore for Context Management

**Why**: Provides fluent interface for managing key-value context items with chainable operations.

```python
# Fluent chaining
service.add_context(model1).add_context(model2)

# Conditional checks
if service.session_context.is_not_empty():
    # Inject into prompt
```

### Event-Driven Context Injection

**Why**: Decouples context management from prompt assembly. Services register hooks that modify payload at specific lifecycle points.

```python
# In service_provider.py boot():
event_bus.on(
    EventType.GATHER_PROJECT_CONTEXT.value,
    session_context_service.add_session_context_hook
)

# Hook implementation:
async def add_session_context_hook(self, payload: Payload) -> Payload:
    session_docs_list = payload.get("session_docs", [])
    session_docs_list.extend(formatted_contexts)
    return payload.set("session_docs", session_docs_list)
```

## API Contracts

### Service Interface

```python
class SessionContextService(Service):
    def add_context(self, model: SessionContextModel) -> "SessionContextService"
    def remove_context(self, key: str) -> "SessionContextService"
    def get_context(self, key: str) -> Optional[SessionContextModel]
    def clear_context(self) -> "SessionContextService"
    def get_all_context(self) -> dict[str, SessionContextModel]
    async def add_session_context_hook(self, payload: Payload) -> Payload
```

**Return Self Pattern**: Enables method chaining for fluent API.

### Command Interface

All commands inherit from `Command` and implement:

```python
@property
def name(self) -> str  # Command trigger (e.g., "ctx:file")

@property
def category(self) -> str  # CLI grouping ("Session Context")

@property
def parser(self) -> ByteArgumentParser  # Argparse configuration

async def execute(self, args: Namespace, raw_args: str) -> None
```

## Integration Points

### With Conventions Domain

**Shared Display**: `CLIContextDisplayService` displays both session context and conventions in side-by-side columns.

```python
# Both use ArrayStore pattern
session_context_service.get_all_context()  # dict[str, SessionContextModel]
convention_context_service.conventions.all()  # dict[str, SkillProperties]
```

**Key Difference**: Conventions are project-scoped (loaded from `.byte/conventions/`), session context is runtime-scoped (stored in `.byte/session_context/`).

### With Web Domain

`WebCommand` depends on `ChromiumService` for headless browser scraping:

```python
chromium_service = self.app.make(ChromiumService)
markdown_content = await chromium_service.do_scrape(url)
```

### With Agent Domain

`WebCommand` optionally uses `CleanerAgent` to extract relevant information from scraped content:

```python
cleaner_agent = self.app.make(CleanerAgent)
result = await cleaner_agent.execute(
    f"# Extract only the relevant information from this web content:\n\n{markdown_content}",
    display_mode="thinking"
)
```

### With Event System

Registers two event hooks in `KnowledgeServiceProvider.boot()`:

1. **GATHER_PROJECT_CONTEXT**: Injects session context into prompt
2. **PRE_PROMPT_TOOLKIT**: Displays context panel in CLI

## Domain-Specific Patterns

### Slugified Keys

All context keys are slugified for safe filesystem usage:

```python
from byte.support.utils import slugify

key = slugify("https://example.com/api/docs")  # "https-example-com-api-docs"
file_path = app.session_context_path(f"{key}.md")
```

### YAML Frontmatter for File Context

When adding files via `/ctx:file`, prepend YAML header for metadata:

```python
yaml_header = f"---\nfile_path: {context_key}\n---\n\n"
content = yaml_header + file_content
```

**Why**: Provides structured metadata for AI to understand context source.

### Graceful Degradation

All file operations handle errors gracefully:

```python
try:
    return self.file_path.read_text(encoding="utf-8")
except (FileNotFoundError, PermissionError, UnicodeDecodeError):
    return ""  # Don't crash, return empty
```

### Boundary-Based Formatting

Use `Boundary` utility for consistent XML tag formatting:

```python
from byte.support import Boundary, BoundaryType

formatted = list_to_multiline_text([
    Boundary.open(BoundaryType.SESSION_CONTEXT, meta={"type": "web", "key": "docs"}),
    content,
    Boundary.close(BoundaryType.SESSION_CONTEXT)
])
```

**Why**: Ensures consistent prompt structure for AI parsing.

## Testing Considerations

- Mock `SessionContextModel.file_path` for file I/O tests
- Use `app.session_context_path()` for path resolution
- Test event hook payload transformations
- Verify ArrayStore state management
- Test command completions for `/ctx:drop`

## Common Pitfalls

1. **Don't confuse with conventions**: Session context is temporary, conventions are permanent
2. **Always slugify keys**: Raw URLs/paths can break filesystem operations
3. **Handle missing files**: Context files may be deleted externally
4. **Clear on session end**: Session context should not persist across Byte restarts (handled by `.byte/session_context/` being temporary)
