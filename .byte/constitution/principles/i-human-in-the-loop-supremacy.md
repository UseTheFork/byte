---
name: I. Human-in-the-Loop Supremacy
---

The human operator MUST retain final authority over all code changes, commits, and agent decisions. No autonomous action may bypass user confirmation for destructive or irreversible operations. Agents exist to augment developer judgment, not replace it. All agent implementations MUST include interrupt points before file writes, git operations, and shell command execution.
