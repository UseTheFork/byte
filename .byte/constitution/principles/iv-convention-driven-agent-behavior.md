---
name: IV. Convention-Driven Agent Behavior
---

All AI agent implementations MUST operate within the boundaries defined by loaded conventions and presets. Agent prompts MUST be assembled dynamically using the convention context system and prompt assembler rather than hardcoded. Presets define read-only files, editable files, and active conventions \u2014 agents MUST NOT modify files outside their granted scope. Rationale: Ensures agent behavior is configurable, auditable, and consistent across sessions.
