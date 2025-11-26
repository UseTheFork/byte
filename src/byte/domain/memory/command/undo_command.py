from argparse import Namespace

from langchain_core.messages import HumanMessage
from langgraph.graph.message import RemoveMessage
from langgraph.graph.state import RunnableConfig

from byte.domain.agent.implementations.coder.agent import CoderAgent
from byte.domain.cli.argparse.base import ByteArgumentParser
from byte.domain.cli.service.command_registry import Command
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.memory.service.memory_service import MemoryService


class UndoCommand(Command):
    """Undo the last conversation step by rolling back to previous checkpoint.

    Reverts the conversation state to the previous checkpoint, effectively
    undoing the last user message and agent response in the current thread.
    """

    @property
    def name(self) -> str:
        return "undo"

    @property
    def category(self) -> str:
        return "Memory"

    @property
    def parser(self) -> ByteArgumentParser:
        parser = ByteArgumentParser(
            prog=self.name,
            description="Undo the last conversation step by removing the most recent human message and all subsequent agent responses from the current thread",
        )
        return parser

    async def execute(self, args: Namespace, raw_args: str) -> None:
        """Execute undo operation on current conversation thread."""
        memory_service = await self.make(MemoryService)
        console = await self.make(ConsoleService)

        # It dosent matter if we use CoderAgent or AskAgent here since they use the same BaseState.
        coder_agent = await self.make(CoderAgent)
        coder_agent_graph = await coder_agent.get_graph()

        memory_service = await self.make(MemoryService)
        thread_id = await memory_service.get_or_create_thread()

        config = RunnableConfig(configurable={"thread_id": thread_id})
        state_snapshot = await coder_agent_graph.aget_state(config)
        messages = state_snapshot.values.get("history_messages", [])

        # Find the most recent HumanMessage index
        last_human_index = None
        for i in range(len(messages) - 1, -1, -1):
            if isinstance(messages[i], HumanMessage):
                last_human_index = i
                break

        # Get all messages from the most recent HumanMessage onwards
        if last_human_index is not None:
            messages_to_remove = messages[last_human_index:]
            remove_messages = [RemoveMessage(id=message.id) for message in messages_to_remove]

            # Display message previews
            max_preview_lines = 5
            console.print()
            console.rule("Messages to Remove")
            console.print()

            for idx, message in enumerate(messages_to_remove):
                message_type = type(message).__name__
                content = str(message.content) if hasattr(message, "content") else str(message)

                # Get first few lines for preview
                lines = content.split("\n")
                preview_lines = lines[:max_preview_lines]

                # Truncate long lines based on console width
                console_width = console.width
                max_line_length = max(40, console_width - 8)
                truncated_lines = []
                for line in preview_lines:
                    if len(line) > max_line_length:
                        truncated_lines.append(line[:max_line_length] + "...")
                    else:
                        truncated_lines.append(line)

                preview_content = "\n".join(truncated_lines)

                # Add ellipsis if there are more lines
                if len(lines) > max_preview_lines:
                    preview_content += "\n..."

                # Create panel for this message
                panel = console.panel(
                    preview_content,
                    title=f"{idx + 1}. {message_type} ({len(lines)} lines)",
                    border_style="secondary",
                )
                console.print(panel)

            num_messages = len(messages_to_remove)
            confirmed = console.confirm(
                f"Remove {num_messages} message{'s' if num_messages != 1 else ''}?", default=True
            )

            if confirmed:
                await coder_agent_graph.aupdate_state(config, {"history_messages": remove_messages})

                console.print_success_panel(
                    "Successfully undone last step",
                    title="Undo",
                )
