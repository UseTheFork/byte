from argparse import Namespace

from langchain.messages import HumanMessage, RemoveMessage
from langgraph.graph.state import RunnableConfig

from byte import ByteArgumentParser, Command
from byte.coder import CoderWorkflow
from byte.memory import MemoryService
from byte.tui import InteractionService, Messages


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
        coder_workflow = self.app.make(CoderWorkflow)
        coder_agent_graph = await coder_workflow.get_graph()

        memory_service = self.app.make(MemoryService)
        thread_id = await memory_service.get_or_create_thread()

        config = RunnableConfig(configurable={"thread_id": thread_id})
        state_snapshot = await coder_agent_graph.aget_state(config)
        messages = state_snapshot.values.get("history_messages", [])

        self.app["log"].info(state_snapshot)
        self.app["log"].info(messages)

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

            num_messages = len(messages_to_remove)
            panel_id: str | None = (
                state_snapshot.metadata.get("panel_id") if state_snapshot.metadata is not None else None
            )

            interaction_service = self.app.make(InteractionService)

            # TODO: Fix the below to use our own protocol to forward events.
            confirmed = await interaction_service.confirm(
                f"This would remove {num_messages} message{'s' if num_messages != 1 else ''} from panel [{panel_id}](action:screen.scroll_to_panel('{panel_id}')). Proceed?"
            )

            if confirmed:
                await coder_agent_graph.aupdate_state(config, {"history_messages": remove_messages})

                if panel_id is not None:
                    self.emit_tui(Messages.RemovePanel(panel_id_to_remove=panel_id))

                await self.notify_success("Successfully undone last step")
