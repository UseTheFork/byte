from typing import Literal, override

from byte.specs.schemas import SpecTask, SpecTaskFiles
from byte.specs.service.spec_loader_service import SpecLoaderService
from byte.tools import BaseTool, ToolResult


class CreateTaskTool(BaseTool):
    name: str = "create_phase_task_tool"
    description: str = (
        "Use this tool to create a new task for a spec. Call this when you want to persist a task with an id, "
        "order, status, content, notes, and file references."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "spec_id": {
                "type": "string",
                "description": "The id of the spec to create the task for.",
                "maxLength": 128,
            },
            "task_id": {
                "type": "string",
                "description": "The unique identifier for the task (e.g., 'lint-files').",
                "maxLength": 128,
            },
            "order": {
                "type": "integer",
                "description": "The numeric order for sequencing this task.",
                "default": 0,
            },
            "status": {
                "type": "string",
                "enum": ["pending", "in_progress", "blocked", "completed"],
                "description": "The current execution status of the task.",
                "default": "pending",
            },
            "content": {
                "type": "string",
                "description": "The body content of the task (written as markdown after the frontmatter).",
            },
            "notes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of notes or observations for the task.",
                "default": [],
            },
            "reference_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Files that should be referenced but not modified.",
                "default": [],
            },
            "create_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Files that need to be created.",
                "default": [],
            },
            "edit_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Files that need to be edited.",
                "default": [],
            },
        },
        "required": ["spec_id", "task_id", "content"],
    }

    @override
    async def run(
        self,
        spec_id: str,
        task_id: str,
        content: str,
        order: int = 0,
        status: Literal["pending", "in_progress", "blocked", "completed"] = "pending",
        notes: list[str] = [],
        reference_files: list[str] = [],
        create_files: list[str] = [],
        edit_files: list[str] = [],
        **kwargs,
    ) -> ToolResult:
        # Validate status
        if status not in ("pending", "in_progress", "blocked", "completed"):
            status = "pending"

        # Create SpecPhaseFiles
        files = SpecTaskFiles(
            reference=reference_files,
            create=create_files,
            edit=edit_files,
        )

        # Create SpecPhase
        task = SpecTask(
            id=task_id,
            order=order,
            status=status,
            content=content,
            notes=notes or [],
            files=files,
        )

        # Save the phase using SpecLoaderService
        spec_loader_service = self.app.make(SpecLoaderService)
        success = spec_loader_service.save_task(spec_id, task)

        if success:
            return ToolResult(result={"content": f"Phase '{task_id}' created for spec '{spec_id}'."})
        else:
            return ToolResult(
                success=False,
                result={"content": f"Failed to create phase '{task_id}' for spec '{spec_id}'."},
            )

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
