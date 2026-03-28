import datetime

from langchain.messages import AIMessage, HumanMessage

from byte.support import Service
from byte.tui.schemas import ChatMessage
from byte.tui.widgets.chatbox import Chatbox


class TUIManagerService(Service):
    """Manages chatbox creation and mounting for agent responses in a single conversation.

    Provides a centralized service for creating and managing chatbox widgets during
    workflow execution. Handles both user messages and agent responses, allowing
    workflows to append content to the chat container without tight coupling to the UI.
    Usage: `chatbox = await manager.create_agent_message("CoderAgent")`
    """

    def boot(self) -> None:
        """Initialize the chatbox manager with empty state.

        Usage: Called automatically during service container boot process
        """
        self.chat_container = None

    def register_container(self, container):
        """Register the chat container for mounting chatboxes.

        Args:
            container: The VerticalScroll container from the Chat widget

        Usage: Called by Chat widget on mount to register the container
        """
        self.chat_container = container

    async def create_user_message(self, content: str):
        """Create and mount a user message chatbox.

        Args:
            content: The user's message text

        Returns:
            The mounted Chatbox widget

        Usage: `chatbox = await manager.create_user_message("Hello")`
        """
        message = ChatMessage(HumanMessage(content), datetime.datetime.now(datetime.UTC))
        chatbox = Chatbox(message)

        if self.chat_container:
            await self.chat_container.mount(chatbox)

        return chatbox

    async def create_agent_message(self, agent_name: str):
        """Create and mount an agent response chatbox with initially empty content.

        Args:
            agent_name: Name of the agent for the chatbox border title

        Returns:
            The mounted Chatbox widget

        Usage: `chatbox = await manager.create_agent_message("CoderAgent")`
        """
        message = ChatMessage(AIMessage(content=""), datetime.datetime.now(datetime.UTC))
        chatbox = Chatbox(message)
        chatbox.border_title = agent_name

        if self.chat_container:
            await self.chat_container.mount(chatbox)

        return chatbox

    async def append_to_chatbox(self, chatbox: Chatbox, content: str):
        """Append content to an existing chatbox.

        Args:
            chatbox: The chatbox widget to update
            content: The content to append

        Usage: `await manager.append_to_chatbox(chatbox, "new text")`
        """
        chatbox.append_chunk(content)
