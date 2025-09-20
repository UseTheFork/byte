# import asyncio
# from typing import Dict, List

# from byte.container import Container
# from byte.core.actors.agent import AgentActor
# from byte.core.actors.base import Actor
# from byte.core.actors.coordinator import CoordinatorActor
# from byte.core.actors.input import InputActor
# from byte.core.actors.message import MessageBus, MessageType
# from byte.core.actors.rendering import RenderingActor


# class ByteActorApp:
#     def __init__(self, container: Container):
#         self.container = container
#         self.message_bus = MessageBus()
#         self.actors: Dict[str, Actor] = {}
#         self.actor_tasks: List[asyncio.Task] = []

#     async def initialize(self):
#         """Initialize all actors and their message subscriptions"""
#         # Create actors
#         self.actors["coordinator"] = CoordinatorActor(self.message_bus, self.container)
#         self.actors["input"] = InputActor(self.message_bus, self.container)
#         self.actors["agent"] = AgentActor(self.message_bus, self.container)
#         self.actors["rendering"] = RenderingActor(self.message_bus, self.container)

#         # Set up message subscriptions
#         self._setup_subscriptions()

#         # Start all actors
#         for actor_name, actor in self.actors.items():
#             task = asyncio.create_task(actor.start())
#             task.set_name(f"actor_{actor_name}")
#             self.actor_tasks.append(task)

#         return self.actor_tasks

#     def _setup_subscriptions(self):
#         """Set up message routing between actors"""
#         # Coordinator subscribes to system-wide events
#         self.message_bus.subscribe("coordinator", MessageType.SHUTDOWN)
#         self.message_bus.subscribe("coordinator", MessageType.STATE_CHANGE)
#         self.message_bus.subscribe("coordinator", MessageType.USER_INPUT)
#         self.message_bus.subscribe("coordinator", MessageType.START_STREAM)
#         self.message_bus.subscribe("coordinator", MessageType.END_STREAM)
#         self.message_bus.subscribe("coordinator", MessageType.COMMAND_INPUT)

#         # Rendering actor subscribes to stream events
#         self.message_bus.subscribe("rendering", MessageType.START_STREAM)
#         self.message_bus.subscribe("rendering", MessageType.STREAM_CHUNK)
#         self.message_bus.subscribe("rendering", MessageType.END_STREAM)
#         self.message_bus.subscribe("rendering", MessageType.CANCEL_STREAM)
#         self.message_bus.subscribe("rendering", MessageType.TOOL_START)
#         self.message_bus.subscribe("rendering", MessageType.TOOL_END)
#         self.message_bus.subscribe("rendering", MessageType.STREAM_ERROR)

#     async def run(self):
#         """Run the actor-based application"""
#         try:
#             tasks = await self.initialize()

#             # Wait for any task to complete (likely shutdown)
#             done, pending = await asyncio.wait(
#                 tasks, return_when=asyncio.FIRST_COMPLETED
#             )

#             # Cancel remaining tasks
#             for task in pending:
#                 task.cancel()

#             # Wait for all tasks to finish
#             await asyncio.gather(*pending, return_exceptions=True)

#         except KeyboardInterrupt:
#             print("\nShutting down...")
#             await self._shutdown()

#     async def _shutdown(self):
#         """Graceful shutdown of all actors"""
#         # Stop all actors
#         for actor in self.actors.values():
#             await actor.stop()

#         # Cancel all tasks
#         for task in self.actor_tasks:
#             if not task.done():
#                 task.cancel()

#         # Wait for tasks to complete
#         await asyncio.gather(*self.actor_tasks, return_exceptions=True)
