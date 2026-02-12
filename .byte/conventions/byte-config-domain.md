---
name: byte-config-domain
description: Domain documentation for src/byte/config - configuration management, versioning, migrations, and repository pattern for application settings.
---

# Config Domain Documentation

## Domain Purpose

Manages application configuration lifecycle: loading, validation, versioning, migration, and type-safe access. Central configuration hub aggregating settings from all domains.

## Key Components

### ByteConfig (byte_config.py)

Root configuration model aggregating all domain configs:

```python
class ByteConfig(BaseModel):
    version: str  # Config schema version
    app: AppConfig
    boot: BootConfig
    cli: CLIConfig
    edit_format: EditFormatConfig
    files: FilesConfig
    git: GitConfig
    lint: LintConfig
    llm: LLMConfig
    lsp: LSPConfig
    presets: Optional[list[PresetsConfig]]
    system: SystemConfig
    web: WebConfig
```

**Pattern**: Each domain provides its own `Config` class imported here. Fields kept alphabetically sorted via `keep-sorted` comments.

### Repository (repository.py)

Type-safe configuration accessor extending `ArrayStore`:

```python
repo.string("llm.model", default="gpt-4")
repo.integer("cli.max_lines", default=100)
repo.boolean("debug", default=False)
repo.array("boot.editable_files", default=[])
```

**Key methods**:

- `string()`, `integer()`, `float()`, `boolean()`, `array()` - Type-safe getters with validation
- `prepend()`, `push()` - Array manipulation
- Raises `ValueError` if type mismatch

### Migrator (migrator.py)

Sequential version-based config migrations:

```python
class BaseMigration(ABC):
    @property
    @abstractmethod
    def target_version(self) -> str: ...

    @abstractmethod
    def migrate(self, config: dict) -> dict: ...
```

**Migration flow**:

1. Discovers `migrations/migration_*.py` files
2. Sorts by `target_version` using semantic versioning
3. Applies migrations where `config.version < migration.target_version`
4. Updates `config.version` after each migration
5. Persists changes to `config.yaml`

**Example migration** (migration_001_000_000.py):

```python
class Migration(BaseMigration):
    @property
    def target_version(self) -> str:
        return "1.0.0"

    def migrate(self, config: dict) -> dict:
        # Restructure llm.model -> llm.main_model.model
        if "model" in config["llm"]:
            old_model = config["llm"]["model"]
            config["llm"]["main_model"] = {"model": old_model}
            config["llm"]["weak_model"] = {"model": old_model}
            del config["llm"]["model"]

        config["version"] = self.target_version
        return config
```

## Data Models

### AppConfig

Runtime application metadata (excluded from serialization):

- `env`: Environment name (production/development)
- `debug`: Debug mode flag
- `version`: Application version

### BootConfig

Initial file context loaded at startup:

- `read_only_files`: Files added to read-only context
- `editable_files`: Files added to editable context

### CLIArgs

Command-line argument overrides for boot config.

## Business Logic

### Configuration Loading

1. Load `config.yaml` from `.byte/config.yaml`
2. Run `Migrator.handle()` to apply pending migrations
3. Parse into `ByteConfig` Pydantic model
4. Validate all nested domain configs
5. Store in `Repository` for type-safe access

### Type Safety Pattern

Repository enforces types at runtime:

```python
# Raises ValueError if not string
value = repo.string("llm.model")

# Prevents bool masquerading as int
count = repo.integer("max_items")  # isinstance(True, int) == True handled
```

### Migration Naming Convention

`migration_XXX_YYY_ZZZ.py` where `XXX.YYY.ZZZ` is semantic version:

- `migration_001_000_000.py` → v1.0.0
- `migration_001_002_003.py` → v1.2.3

## API Contracts

### Repository Interface

```python
def string(key: str, default: str | Callable | None) -> str
def integer(key: str, default: int | Callable | None) -> int
def float(key: str, default: float | Callable | None) -> float
def boolean(key: str, default: bool | Callable | None) -> bool
def array(key: str, default: list | Callable | None) -> list
def prepend(key: str, value: Any) -> None
def push(key: str, value: Any) -> None
```

### Migration Interface

```python
class BaseMigration(ABC):
    @property
    def target_version(self) -> str: ...
    def migrate(self, config: dict) -> dict: ...
```

## Domain Patterns

### Lazy Import Pattern

`__init__.py` uses dynamic imports via `_dynamic_imports` dict and `__getattr__`:

```python
_dynamic_imports = {
    "ByteConfig": "byte_config",
    "Migrator": "migrator",
}

def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result
```

### Pydantic Field Exclusion

Runtime-only fields use `exclude=True`:

```python
version: str = Field(default="0.0.0", exclude=True)
```

Prevents serialization back to YAML.

### Alphabetical Sorting

Config fields wrapped in `keep-sorted` comments for pre-commit hook:

```python
# keep-sorted start
app: AppConfig
boot: BootConfig
cli: CLIConfig
# keep-sorted end
```

## Integration Points

### With Foundation

- `Application.config_path()` - Resolves `.byte/config.yaml`
- `Application.app_path()` - Resolves migration files
- `Application["console"]` - Prints migration progress

### With Support

- `ArrayStore` - Base class for `Repository`
- `Yaml.save()` - Persists migrated config

### With All Domains

Each domain exports a `Config` class imported by `ByteConfig`:

- `byte.cli.config.CLIConfig`
- `byte.llm.config.LLMConfig`
- `byte.files.config.FilesConfig`
- etc.

## Exception Handling

`ByteConfigException` - Base for config errors (validation, missing settings).

Inherits from `byte.foundation.ByteException`.
