---
name: parsing-domain
description: Domain documentation for src/byte/parsing - skill file parsing and validation. Use when working with SKILL.md files, frontmatter parsing, or skill metadata validation.
---

# Parsing Domain Documentation

## Domain Purpose

Parses and validates SKILL.md files with YAML frontmatter. Ensures skill metadata conforms to naming conventions, length limits, and required field constraints.

## Key Components

### SkillParsingService

Core service for parsing SKILL.md files. Handles:

- YAML frontmatter extraction
- Metadata validation
- Skill content reading

### SkillValidator

Agent validator that validates skill content during agent execution. Integrates with agent validation pipeline.

### SkillProperties

Data model representing parsed skill metadata with `name`, `description`, `location`, and optional `metadata` dict.

## Data Models

```python
@dataclass
class SkillProperties:
    name: str              # kebab-case, max 64 chars
    description: str       # max 1024 chars
    location: str          # file path
    metadata: dict[str, str] | None  # optional key-value pairs
```

## Business Logic

### Frontmatter Format

```markdown
---
name: skill-name
description: What the skill does
metadata:
  key: value
---

Markdown body content
```

### Validation Rules

**Name validation:**

- Lowercase only
- Max 64 characters
- Letters, digits, hyphens (Unicode letters supported via NFKC normalization)
- Cannot start/end with hyphen
- No consecutive hyphens

**Description validation:**

- Non-empty string
- Max 1024 characters

**Allowed frontmatter fields:** `name`, `description`, `metadata`

### Error Handling

- `ParseError`: Invalid YAML, missing frontmatter delimiters
- `ValidationError`: Missing required fields, invalid format

## API Contracts

### SkillParsingService

```python
# Parse frontmatter from content
metadata, body = service.parse_frontmatter(content: str) -> tuple[dict, str]

# Read and validate properties from file
properties = service.read_properties(skill_path: Path) -> SkillProperties

# Read validated skill content (body only)
content = service.read_skill_content(skill_path: str | Path) -> str

# Validation methods (return list of error strings)
errors = service.validate_name(name: str) -> list[str]
errors = service.validate_description(description: str) -> list[str]
errors = service.validate_metadata_fields(metadata: dict) -> list[str]
errors = await service.validate_metadata(metadata: dict, skill_dir: Path | None) -> list[str]
```

### SkillValidator

```python
# Validate agent state containing skill content
errors = await validator.validate(state: BaseState) -> list[ValidationError | None]
```

## Patterns & Conventions

**Separation of concerns:**

- `parse_frontmatter()`: Pure parsing, no validation
- `read_properties()`: Parsing + minimal validation (required fields only)
- `validate_*()`: Granular validation methods
- `validate_metadata()`: Comprehensive validation

**Error accumulation:** Validation methods return `list[str]` to collect all errors, not fail-fast.

**Unicode normalization:** Names normalized with NFKC before validation to handle i18n characters consistently.

**Metadata coercion:** `metadata` dict values coerced to strings during parsing.

**Constants:**

```python
MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
ALLOWED_FIELDS = {"name", "description", "metadata"}
```

## Integration Points

**Agent domain:** `SkillValidator` integrates with agent validation pipeline via `Validator` base class.

**Foundation:** Uses `ByteException` for domain exceptions, `Service` base class, `ServiceProvider` pattern.

**Support utilities:** Uses `extract_content_from_message()`, `get_last_message()` for agent state processing.
