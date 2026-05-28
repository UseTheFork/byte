from typing import override

from byte.specs.schemas import SpecTask, SpecTaskFiles
from byte.specs.service.spec_loader_service import SpecLoaderService
from byte.tools import BaseTool, ToolResult
from byte.tools.exceptions import ToolRunException, ToolValidationException


class EditTaskTool(BaseTool):
    name: str = "edit_task_tool"
    description: str = (
        "Use this tool to edit an existing task for a spec. Call this when you want to update a task's "
        "order, status, content, notes, or file references."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "spec_id": {
                "type": "string",
                "description": "The id of the spec containing the task.",
                "maxLength": 128,
            },
            "task_id": {
                "type": "string",
                "description": "The unique identifier for the task to edit.",
                "maxLength": 128,
            },
            "order": {
                "type": "integer",
                "description": "The numeric order for sequencing this task.",
            },
            "status": {
                "type": "string",
                "enum": ["pending", "in_progress", "blocked", "completed"],
                "description": "The current execution status of the task.",
            },
            "content": {
                "type": "string",
                "description": "The body content of the task (written as markdown after the frontmatter).",
            },
            "notes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of notes or observations for the task.",
            },
            "reference_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Files that should be referenced but not modified.",
            },
            "create_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Files that need to be created.",
            },
            "edit_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Files that need to be edited.",
            },
        },
        "required": ["spec_id", "task_id"],
    }

    @override
    async def run(
        self,
        spec_id: str,
        task_id: str,
        order: int | None = None,
        status: str | None = None,
        content: str | None = None,
        notes: list[str] | None = None,
        reference_files: list[str] | None = None,
        create_files: list[str] | None = None,
        edit_files: list[str] | None = None,
        **kwargs,
    ) -> ToolResult:
        spec_loader_service = self.app.make(SpecLoaderService)

        # Load the existing task
        existing_task = spec_loader_service.load_task(spec_id, task_id)
        if existing_task is None:
            raise ToolValidationException(
                f"Task '{task_id}' not found in spec '{spec_id}'.",
            )

        # Prepare updated values, preserving existing values if not provided
        updated_order = order if order is not None else existing_task.order
        updated_status = status if status is not None else existing_task.status
        updated_content = content if content is not None else existing_task.content
        updated_notes = notes if notes is not None else existing_task.notes
        updated_reference_files = reference_files if reference_files is not None else existing_task.files.reference
        updated_create_files = create_files if create_files is not None else existing_task.files.create
        updated_edit_files = edit_files if edit_files is not None else existing_task.files.edit

        # Validate status
        if updated_status not in ("pending", "in_progress", "blocked", "completed"):
            updated_status = "pending"

        # Create updated SpecTaskFiles
        files = SpecTaskFiles(
            reference=updated_reference_files,
            create=updated_create_files,
            edit=updated_edit_files,
        )

        # Create updated SpecTask
        task = SpecTask(
            id=task_id,
            order=updated_order,
            status=updated_status,
            content=updated_content,
            notes=updated_notes,
            files=files,
        )

        # Save the task using SpecLoaderService
        success = spec_loader_service.save_task(spec_id, task)

        if success:
            return ToolResult(result={"content": f"Task '{task_id}' updated for spec '{spec_id}'."})
        else:
            raise ToolRunException(f"Failed to update task '{task_id}' for spec '{spec_id}'.")

    @classmethod
    def format_tool_message(cls, result: ToolResult) -> str:
        return result.result.get("content", "")
