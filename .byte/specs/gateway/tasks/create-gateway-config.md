---
files:
  create:
  - src/byte/gateway/config.py
  edit:
  - src/byte/config/byte_config.py
  reference:
  - src/byte/llm/config.py
  - src/byte/tui/config.py
  - src/byte/foundation/bootstrap/prepare_environment.py
id: create-gateway-config
notes: []
order: 2
status: completed
---
# Gateway Domain — `config.py`

**Goal:** Define `GatewayConfig` and integrate it into `ByteUserConfig` so the gateway's enable/host/port settings are loaded from `config.jsonc`.
**Architecture:** Follow the exact pattern used by `LLMConfig` and `TUIConfig`. `GatewayConfig` is a standalone Pydantic model; `ByteUserConfig` gains a `gateway` field.

---

## 1. Create `src/byte/gateway/config.py`

```python
from pydantic import BaseModel


class GatewayConfig(BaseModel):
    """Gateway domain configuration."""

    enable: bool = False
    host: str = "127.0.0.1"
    port: int = 9731
```

## 2. Edit `src/byte/config/byte_config.py`

Add the import at the top alongside the other domain config imports:

```python
from byte.gateway.config import GatewayConfig
```

Then add the field inside `ByteUserConfig`, keeping the `# keep-sorted` block alphabetically ordered:

```python
gateway: GatewayConfig = Field(default_factory=GatewayConfig)
```

The final sorted field list in `ByteUserConfig` should look like:

```python
# keep-sorted start
files: FilesConfig = Field(default_factory=FilesConfig)
gateway: GatewayConfig = Field(default_factory=GatewayConfig)
git: GitConfig = Field(default_factory=GitConfig)
lint: LintConfig = Field(default_factory=LintConfig, description="Code linting and formatting configuration")
llm: LLMConfig = Field(default_factory=LLMConfig)
presets: Optional[list[PresetsConfig]] = Field(default_factory=list)
tui: TUIConfig = Field(default_factory=TUIConfig)
web: WebConfig = Field(default_factory=WebConfig)
# keep-sorted end
```

> `ByteUserConfig.model_fields` is automatically populated by Pydantic — no manual registration is needed. The field will be included in `config.jsonc` serialization because `PrepareEnvironment._setup_config` uses `include=user_fields` where `user_fields = set(ByteUserConfig.model_fields.keys())`.
