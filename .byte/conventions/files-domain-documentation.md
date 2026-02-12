---
name: files-domain-documentation
description: Domain documentation for src/byte/files - file context management, project discovery, and file watching. Use when working with file operations, AI context management, or understanding the files domain architecture.
---

# Files Domain Documentation

## Domain Purpose

The **files domain** manages AI context through file tracking, project discovery, and file system monitoring. It provides:

- **File Context Management**: Track which files AI can read/modify with mode-based permissions
- **Project Discovery**: Fast file lookup with gitignore-aware caching
- **File Watching**: Real-time monitoring for AI comment markers and file changes
- **Intelligent Completions**: Tab completion from discovered project files

## Core Components

### Models (`models.py`)

**FileMode Enum**: Two access levels for AI context

- `READ_ONLY`: AI can reference but not modify
- `EDITABLE`: AI can modify via SEARCH/REPLACE blocks

**FileContext**: Immutable file metadata container

```python
FileContext(path=Path, mode=FileMode, root_path=Path)
# Properties: language, relative_path, get_content()
```

### Services

#### FileService (`service/file_service.py`)

**Central orchestrator** for file context operations.

Key responsibilities:

- Maintain `_context_files` dict mapping absolute paths to FileContext
- Add/remove files with wildcard support: `add_file("src/*.py", mode)`
- Generate AI prompts with file content wrapped in boundaries
- Provide project hierarchy tree for LLM understanding
- Emit events for file additions (EventType.FILE_ADDED)

**Critical patterns**:

- Always resolve paths to absolute before dict lookup
- Only add files present in FileDiscoveryService (ensures gitignore compliance)
- Separate read-only and editable files in prompt generation
- Use Boundary markers for structured file content

#### FileDiscoveryService (`service/discovery_service.py`)

**Caches all project files** on boot for fast operations.

Key responsibilities:

- Scan project directory once, store in `_all_files: Set[Path]`
- Provide fuzzy file matching for completions
- Filter by extension for language-specific operations
- Maintain cache consistency via FileWatcherService events

**Performance pattern**: Single scan on boot, incremental updates via watcher

#### FileIgnoreService (`service/ignore_service.py`)

**Centralized ignore pattern management** combining .gitignore + config.

Key responsibilities:

- Load patterns from `.gitignore` and `config.files.ignore`
- Compile into single `pathspec.PathSpec` for efficient matching
- Check both file and parent directory patterns
- Provide synchronous `is_ignored()` for watcher filter

**Pattern**: Load once on boot, expose pathspec for reuse

#### FileWatcherService (`service/watcher_service.py`)

**Monitors filesystem changes** to keep discovery cache current.

Key responsibilities:

- Use `watchfiles.awatch()` with custom filter function
- Update FileDiscoveryService cache on add/delete
- Emit EventType.FILE_CHANGED for other services
- Run as background task via TaskManager

**Critical**: Filter function must be synchronous (watchfiles requirement)

#### AICommentWatcherService (`service/ai_comment_watcher_service.py`)

**Detects AI comment markers** to trigger automatic agent actions.

Marker types:

- `AI:` or `AI!` → CoderAgent (execute task)
- `AI?` → AskAgent (answer question)
- `AI@` → Add file as read-only

Key responsibilities:

- Scan file content for comment blocks with AI markers
- Auto-add files to context when markers detected
- Interrupt prompt toolkit to inject AI instructions
- Add reinforcement prompts based on agent type

**Pattern**: Event-driven via FILE_CHANGED → scan → interrupt if markers found

### Commands

All commands in `command/` follow consistent patterns:

**Tab Completion Strategy**:

- `AddFileCommand`, `ReadOnlyCommand`: Complete from discovered files NOT in context
- `DropFileCommand`, `SwitchModeCommand`: Complete from files IN context
- Use `FileService.find_project_files()` for discovery-based completions

**Command Patterns**:

```python
# Add files (editable or read-only)
await file_service.add_file(path, FileMode.EDITABLE)

# Remove files
await file_service.remove_file(path)

# Switch mode (toggle between read-only/editable)
await file_service.set_file_mode(path, new_mode)

# List files by mode
files = file_service.list_files(FileMode.EDITABLE)
```

### Tools

**read_files** (`tools/read_files.py`): LangChain tool for AI to read project files

- Accepts list of relative paths
- Returns content wrapped in FILE boundaries
- Does NOT require files to be in context (reads from discovery)

## Data Flow

### File Addition Flow

```
User: /add src/main.py
  ↓
AddFileCommand.execute()
  ↓
FileService.add_file()
  ├→ Check FileDiscoveryService (is file discovered?)
  ├→ Resolve to absolute path
  ├→ Add to _context_files dict
  └→ Emit FILE_ADDED event
```

### File Discovery Flow

```
Boot
  ↓
FileIgnoreService.boot() → Load .gitignore + config patterns
  ↓
FileDiscoveryService.boot() → Scan project, filter via ignore service
  ↓
FileWatcherService._start_watching() → Monitor changes
  ↓
On file change → Update discovery cache → Emit FILE_CHANGED
```

### AI Comment Detection Flow

```
File modified
  ↓
FileWatcherService detects change → Emit FILE_CHANGED
  ↓
AICommentWatcherService.handle_file_change()
  ├→ Scan for AI: / AI@ / AI! / AI? markers
  ├→ Auto-add file to context with appropriate mode
  └→ Interrupt prompt toolkit if markers found
  ↓
modify_user_request_hook() → Inject AI instruction prompt
  ↓
add_reinforcement_hook() → Add agent-specific instructions
```

## API Contracts

### FileService Public API

```python
# Context management
async def add_file(path: str | PathLike, mode: FileMode) -> bool
async def remove_file(path: str | PathLike) -> bool
async def set_file_mode(path: str | PathLike, mode: FileMode) -> bool
def list_files(mode: Optional[FileMode] = None) -> List[FileContext]
def get_file_context(path: str | PathLike) -> Optional[FileContext]
async def clear_context() -> None

# Prompt generation
async def generate_context_prompt() -> tuple[list[str], list[str]]
async def generate_context_prompt_with_line_numbers() -> tuple[list[str], list[str]]
async def generate_project_hierarchy() -> str

# Discovery integration
async def get_project_files(extension: Optional[str] = None) -> List[str]
async def find_project_files(pattern: str) -> List[str]
async def is_file_in_context(path: str | PathLike) -> bool
```

### FileDiscoveryService Public API

```python
async def get_files(extension: Optional[str] = None) -> List[Path]
async def get_relative_paths(extension: Optional[str] = None) -> List[str]
async def find_files(pattern: str) -> List[Path]  # Fuzzy matching
async def add_file(path: Path) -> bool
async def remove_file(path: Path) -> bool
async def refresh() -> None
```

### FileIgnoreService Public API

```python
def is_ignored(path: Path) -> bool
async def refresh() -> None
def get_pathspec() -> Optional[pathspec.PathSpec]
```

## Domain Patterns

### Wildcard Support Pattern

Both `add_file()` and `remove_file()` support glob patterns:

```python
await file_service.add_file("src/**/*.py", FileMode.EDITABLE)
await file_service.remove_file("tests/*.py")
```

Implementation: Detect `*`, `?`, `[` in path → use `glob.glob()` → iterate matches

### Path Resolution Pattern

**Always resolve to absolute paths** before dict operations:

```python
if not Path(path).is_absolute():
    path_obj = self.app.root_path(str(path)).resolve()
else:
    path_obj = Path(path).resolve()
key = str(path_obj)  # Dict key is absolute path string
```

### Boundary Wrapping Pattern

File content in prompts uses structured boundaries:

```python
Boundary.open(BoundaryType.FILE, meta={
    "source": relative_path,
    "language": language,
    "mode": "editable"  # or "read-only"
})
# Content with code fences
Boundary.close(BoundaryType.FILE)
```

### Event-Driven Updates Pattern

Services communicate via EventBus:

- `FILE_ADDED`: FileService → notify file added to context
- `FILE_CHANGED`: FileWatcherService → notify file modified/added/deleted
- `PRE_PROMPT_TOOLKIT`: Display context files before prompt
- `POST_PROMPT_TOOLKIT`: Check for AI comment markers

### Discovery Cache Pattern

FileDiscoveryService maintains `_all_files: Set[Path]`:

- Populated once on boot via recursive scan
- Updated incrementally via FileWatcherService events
- Provides O(1) membership checks, fast iteration
- Respects gitignore via FileIgnoreService filter

## Integration Points

### With Agent Domain

- `generate_context_prompt()` → Provides file content for agent prompts
- `generate_context_prompt_with_line_numbers()` → For research agent LSP operations
- AI comment markers trigger CoderAgent or AskAgent

### With CLI Domain

- Commands registered via FileServiceProvider
- Tab completions use discovery service
- `list_in_context_files_hook()` displays files before each prompt

### With Code Operations Domain

- Editable files enable SEARCH/REPLACE blocks
- File mode determines AI modification permissions

### With Git Domain

- File discovery respects .gitignore patterns
- Context files used for commit message generation

### With Knowledge Domain

- Files can be added to session context
- Context service may reference file content

## Configuration

**FilesConfig** (`config.py`):

```python
files:
  watch:
    enable: bool  # Enable AI comment watching
  ignore: List[str]  # Additional gitignore patterns
```

Default ignore patterns: `.byte/cache`, `.ruff_cache`, `.idea`, `.venv`, `.git`, `__pycache__`, `node_modules`, `dist`

## Key Design Decisions

1. **Separate Discovery from Context**: Discovery caches ALL project files; context tracks only AI-visible files
2. **Mode-Based Permissions**: Explicit read-only vs editable prevents accidental modifications
3. **Absolute Path Keys**: Dict keys are absolute paths to avoid ambiguity
4. **Single Ignore Service**: Centralized pattern management prevents inconsistencies
5. **Event-Driven Architecture**: Loose coupling via EventBus for extensibility
6. **Wildcard Support**: Enables bulk operations without iteration in user code
7. **Fuzzy Matching**: Prioritizes exact prefix matches, then relevance-scored fuzzy matches
8. **AI Comment Markers**: Enables file-based task specification without CLI interaction

## Testing Considerations

- Mock FileDiscoveryService for unit tests (avoid filesystem scans)
- Use temporary directories for integration tests
- Test wildcard patterns with various glob scenarios
- Verify gitignore pattern matching edge cases
- Test AI comment marker detection across comment styles
