from enum import Enum

from byte.core.actors.base import Actor
from byte.core.actors.message import Message, MessageType


class AppState(Enum):
    IDLE = "idle"
    PROCESSING_INPUT = "processing_input"
    AGENT_THINKING = "agent_thinking"
    AGENT_STREAMING = "agent_streaming"
    EXECUTING_COMMAND = "executing_command"
    FILE_WATCHING = "file_watching"
    SHUTTING_DOWN = "shutting_down"


class CoordinatorActor(Actor):
    def __init__(self, name: str, message_bus, container=None):
        super().__init__(name, message_bus, container)
        self.current_state = AppState.IDLE
        self.valid_transitions = {
            AppState.IDLE: {
                AppState.PROCESSING_INPUT,
                AppState.FILE_WATCHING,
                AppState.SHUTTING_DOWN,
            },
            AppState.PROCESSING_INPUT: {
                AppState.AGENT_THINKING,
                AppState.EXECUTING_COMMAND,
                AppState.IDLE,
            },
            AppState.AGENT_THINKING: {AppState.AGENT_STREAMING, AppState.IDLE},
            AppState.AGENT_STREAMING: {AppState.IDLE, AppState.EXECUTING_COMMAND},
            AppState.EXECUTING_COMMAND: {AppState.IDLE, AppState.AGENT_THINKING},
            AppState.FILE_WATCHING: {AppState.PROCESSING_INPUT, AppState.IDLE},
            AppState.SHUTTING_DOWN: set(),  # Terminal state
        }
        self.shutdown_requested = False

    async def handle_message(self, message: Message):
        if message.type == MessageType.SHUTDOWN:
            await self._handle_shutdown(message)
        elif message.type == MessageType.STATE_CHANGE:
            await self._handle_state_change(message)
        elif message.type == MessageType.USER_INPUT:
            await self._transition_to(AppState.PROCESSING_INPUT)
        elif message.type == MessageType.START_STREAM:
            await self._transition_to(AppState.AGENT_STREAMING)
        elif message.type == MessageType.END_STREAM:
            await self._transition_to(AppState.IDLE)
        elif message.type == MessageType.COMMAND_INPUT:
            await self._transition_to(AppState.EXECUTING_COMMAND)

    async def _handle_shutdown(self, message: Message):
        """Handle shutdown request"""
        self.shutdown_requested = True
        await self._transition_to(AppState.SHUTTING_DOWN)

        # Broadcast shutdown to all actors
        await self.broadcast(
            Message(type=MessageType.SHUTDOWN, payload=message.payload)
        )

    async def _handle_state_change(self, message: Message):
        """Handle explicit state change requests"""
        new_state_str = message.payload.get("new_state")
        if new_state_str:
            try:
                new_state = AppState(new_state_str)
                await self._transition_to(new_state)
            except ValueError:
                await self.on_error(ValueError(f"Invalid state: {new_state_str}"))

    async def _transition_to(self, new_state: AppState):
        """Transition to new state if valid"""
        if new_state in self.valid_transitions[self.current_state]:
            old_state = self.current_state
            self.current_state = new_state

            # Notify about state change
            await self.broadcast(
                Message(
                    type=MessageType.STATE_CHANGE,
                    payload={
                        "old_state": old_state.value,
                        "new_state": new_state.value,
                    },
                )
            )

            await self._on_state_enter(new_state, old_state)
        else:
            print(f"Invalid transition from {self.current_state} to {new_state}")

    async def _on_state_enter(self, new_state: AppState, old_state: AppState):
        """Handle state entry logic"""
        if new_state == AppState.SHUTTING_DOWN:
            # Begin shutdown sequence
            await self.stop()

    async def on_idle(self):
        """Periodic maintenance during idle periods"""
        if self.shutdown_requested and self.current_state != AppState.SHUTTING_DOWN:
            await self._transition_to(AppState.SHUTTING_DOWN)
