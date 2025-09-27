# import asyncio
# from typing import Dict

# from byte import log
# from byte.core.actors.base import Actor
# from byte.core.actors.message import Message, MessageType
# from byte.core.actors.streams import StreamManager
# from byte.core.service.mixins import UserInteractive
# from byte.domain.agent.coder.agent import CoderAgent
# from byte.domain.agent.service.agent_service import AgentService
# from byte.domain.cli_output.actor.rendering_actor import RenderingActor
# from byte.domain.system.actor.coordinator_actor import CoordinatorActor


# class AgentActor(Actor, UserInteractive):
#     async def boot(self):
#         await super().boot()
#         self.stream_manager = StreamManager(self.message_bus.get_queue(RenderingActor))
#         # Track accumulated tool call chunks for proper parsing
#         self.accumulated_tool_calls: Dict[str, Dict] = {}

#     async def handle_message(self, message: Message):
#         if message.type == MessageType.SHUTDOWN:
#             await self.stop()
#         elif message.type == MessageType.USER_INPUT:
#             await self._handle_user_input(message)
#         elif message.type == MessageType.AGENT_REQUEST:
#             await self._handle_agent_request(message)
#         elif message.type == MessageType.CANCEL_STREAM:
#             await self._handle_cancel_stream(message)

#     async def _handle_user_input(self, message: Message):
#         """Handle user input by routing to appropriate agent"""
#         user_input = message.payload["input"]
#         agent_type = message.payload.get("agent_type", "coder")

#         await self.send_to(
#             CoordinatorActor,
#             Message(
#                 type=MessageType.AGENT_REQUEST,
#                 payload={
#                     "action": "start_thinking",
#                     "agent_type": agent_type,
#                     "user_input": user_input,
#                 },
#             ),
#         )

#         # Create new stream for this request
#         stream_id = self.stream_manager.create_stream(
#             stream_type="agent", agent_type=agent_type, user_input=user_input
#         )

#         # Start processing in background
#         asyncio.create_task(
#             self._process_agent_request(stream_id, agent_type, user_input)
#         )

#     async def _handle_agent_request(self, message: Message):
#         """Handle direct agent requests"""
#         # Similar to user input but for programmatic requests
#         pass

#     async def _handle_cancel_stream(self, message: Message):
#         """Handle stream cancellation requests"""
#         stream_id = message.payload.get("stream_id")
#         if stream_id:
#             await self.stream_manager.cancel_stream(stream_id)

#     async def _process_agent_request(
#         self, stream_id: str, agent_type: str, user_input: str
#     ):
#         """Process agent request using astream_events for comprehensive streaming"""
#         try:
#             # Start the stream
#             await self.stream_manager.start_stream(stream_id)

#             await self._handle_on_chat_model_start(stream_id, agent_type)

#             # Get agent service and create the agent instance
#             agent_service = await self.make(AgentService)
#             agent_class = CoderAgent  # This would be dynamic based on agent_type

#             # Get the agent instance (not the graph directly)
#             if agent_class not in agent_service._agent_instances:
#                 agent_instance = await self.make(agent_class)
#                 agent_service._agent_instances[agent_class] = agent_instance

#             agent = agent_service._agent_instances[agent_class]

#             # Clear any previous tool call state for this stream
#             self.accumulated_tool_calls.clear()

#             # Use the agent's stream method which returns astream_events
#             async for event in agent.stream(user_input):
#                 await self._handle_stream_event(stream_id, event)

#             # Finish the stream
#             await self.stream_manager.finish_stream(stream_id)

#             await self.send_to(
#                 CoordinatorActor,
#                 Message(
#                     type=MessageType.END_STREAM,
#                     payload={"stream_id": stream_id, "success": True},
#                 ),
#             )

#         except Exception as e:
#             log.error(f"Agent processing error: {e}")
#             # Handle stream error
#             if stream_id in self.stream_manager.active_streams:
#                 await self.stream_manager.active_streams[stream_id].error(e)

#             await self.send_to(
#                 CoordinatorActor,
#                 Message(
#                     type=MessageType.STREAM_ERROR,
#                     payload={"stream_id": stream_id, "error": str(e)},
#                 ),
#             )

#         finally:
#             # Cleanup completed streams periodically
#             self.stream_manager.cleanup_completed_streams()
#             await self.prompt_for_input()

#     async def _handle_stream_event(self, stream_id: str, event: dict):
#         """Route different event types to appropriate handlers"""
#         event_type = event["event"]

#         # dump(event)

#         # [21:31:42] INFO     Name: LangGraph | Type: on_chain_start |  Type: ea212a5a-41bf-4d11-8433-b3d0897ea4f4 |                                                                                     agent_actor.py:203
#         #            INFO     Name: fetch_file_context | Type: on_chain_start |  Type: 2de7049f-231c-42e9-bcdf-c0a9a75b76f2 |                                                                            agent_actor.py:203
#         #            INFO     Name: fetch_file_context | Type: on_chain_stream |  Type: 2de7049f-231c-42e9-bcdf-c0a9a75b76f2 |                                                                           agent_actor.py:203
#         #            INFO     Name: fetch_file_context | Type: on_chain_end |  Type: 2de7049f-231c-42e9-bcdf-c0a9a75b76f2 |                                                                              agent_actor.py:203
#         #            INFO     Name: LangGraph | Type: on_chain_stream |  Type: ea212a5a-41bf-4d11-8433-b3d0897ea4f4 |                                                                                    agent_actor.py:203
#         #            INFO     Name: assistant | Type: on_chain_start |  Type: aca1aed8-53d5-4569-b3ef-90d3d87c884a |                                                                                     agent_actor.py:203
#         #            INFO     Name: RunnableSequence | Type: on_chain_start |  Type: b887720a-8010-4b56-a53b-ce8c1bbfe148 |                                                                              agent_actor.py:203
#         #            INFO     Name: ChatPromptTemplate | Type: on_prompt_start |  Type: e1f1a7fb-2363-4803-a701-9d3bb26bac50 |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatPromptTemplate | Type: on_prompt_end |  Type: e1f1a7fb-2363-4803-a701-9d3bb26bac50 |                                                                             agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_start |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                            agent_actor.py:203
#         # ⠙ Thinking...[21:31:45] INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f | (Tool call starts here.)                                                                          agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         # [21:31:46] INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         # [21:31:47] INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         # I need to think of a good long question to test the user_confirm tool. Let me ask you something comprehensive about a software development scenario that would require confirmation.

#         # ▶ user_confirm
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         # [21:31:52] INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         # INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_stream |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                           agent_actor.py:203
#         #            INFO     Name: ChatAnthropic | Type: on_chat_model_end |  Type: d0c1bba2-f537-4a68-97af-da4f0e54d39f |                                                                              agent_actor.py:203
#         #            INFO     Name: RunnableSequence | Type: on_chain_end |  Type: b887720a-8010-4b56-a53b-ce8c1bbfe148 |                                                                                agent_actor.py:203
#         #            INFO     Name: _should_continue | Type: on_chain_start |  Type: 893a46f8-b773-446c-b5cf-b6924b8fd38d |                                                                              agent_actor.py:203
#         #            INFO     Name: _should_continue | Type: on_chain_end |  Type: 893a46f8-b773-446c-b5cf-b6924b8fd38d |                                                                                agent_actor.py:203
#         #            INFO     Name: assistant | Type: on_chain_stream |  Type: aca1aed8-53d5-4569-b3ef-90d3d87c884a |                                                                                    agent_actor.py:203
#         #            INFO     Name: assistant | Type: on_chain_end |  Type: aca1aed8-53d5-4569-b3ef-90d3d87c884a |                                                                                       agent_actor.py:203
#         #            INFO     Name: LangGraph | Type: on_chain_stream |  Type: ea212a5a-41bf-4d11-8433-b3d0897ea4f4 |                                                                                    agent_actor.py:203
#         #            INFO     Name: tools | Type: on_chain_start |  Type: b51ad700-0092-4a39-ad9f-e71dccc7c56b |                                                                                         agent_actor.py:203
#         #            INFO     Name: user_confirm | Type: on_tool_start |  Type: 8a9340fa-ff39-4a36-8783-a304e898ffda |                                                                                   agent_actor.py:203

#         # log.info(
#         #     f"Name: {event['name']} | Type: {event_type} |  Type: {event['run_id']} | "
#         # )

#         if event_type == "on_chat_model_stream":
#             await self._handle_chat_model_stream(stream_id, event)
#         elif event_type == "on_chat_model_start":
#             # Model started thinking - could show spinner
#             pass
#         elif event_type == "on_tool_start":
#             await self._handle_tool_start(stream_id, event)
#         elif event_type == "on_tool_end":
#             await self._handle_tool_end(stream_id, event)

#     async def _handle_chat_model_stream(self, stream_id: str, event: dict):
#         """Handle streaming chunks from the chat model"""
#         chunk = event["data"]["chunk"]

#         # Handle tool call chunks if present
#         if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
#             await self._handle_tool_call_chunks(stream_id, chunk.tool_call_chunks)

#         # Handle regular text content
#         text_content = self._extract_text_content(chunk)
#         if text_content:
#             await self.stream_manager.process_chunk(
#                 stream_id, {"data": {"chunk": chunk}, "type": "text"}
#             )

#     async def _handle_tool_call_chunks(self, stream_id: str, tool_call_chunks: list):
#         """Handle streaming tool call chunks with accumulation - single tool call only"""
#         for tool_chunk in tool_call_chunks:
#             tool_id = tool_chunk.get("id")
#             tool_name = tool_chunk.get("name")
#             tool_args = tool_chunk.get("args", "")

#             # Use single key since we only process one tool call at a time
#             call_key = "current_tool"

#             # Initialize or update accumulated state
#             if call_key not in self.accumulated_tool_calls:
#                 self.accumulated_tool_calls[call_key] = {
#                     "id": tool_id,
#                     "name": tool_name,
#                     "args": "",
#                     "complete": False,
#                 }

#             # Accumulate arguments
#             if tool_args:
#                 self.accumulated_tool_calls[call_key]["args"] += tool_args

#             # Update name and id if we didn't have them before or if they're provided
#             if tool_name and not self.accumulated_tool_calls[call_key]["name"]:
#                 self.accumulated_tool_calls[call_key]["name"] = tool_name
#             if tool_id and not self.accumulated_tool_calls[call_key]["id"]:
#                 self.accumulated_tool_calls[call_key]["id"] = tool_id

#             # Broadcast tool call chunk for real-time display
#             await self.broadcast(
#                 Message(
#                     type=MessageType.TOOL_CALL_CHUNK,
#                     payload={
#                         "stream_id": stream_id,
#                         "tool_name": self.accumulated_tool_calls[call_key]["name"],
#                         "tool_args": self.accumulated_tool_calls[call_key]["args"],
#                         "tool_id": self.accumulated_tool_calls[call_key]["id"],
#                         "is_partial": True,
#                         "call_key": call_key,
#                     },
#                 )
#             )

#     async def _handle_on_chat_model_start(self, stream_id: str, agent_type: str):
#         """Handle tool execution start"""
#         await self.send_to(
#             CoordinatorActor,
#             Message(
#                 type=MessageType.START_STREAM,
#                 payload={"stream_id": stream_id, "agent_type": agent_type},
#             ),
#         )

#     async def _handle_tool_start(self, stream_id: str, event: dict):
#         """Handle tool execution start"""
#         tool_name = event["name"]
#         await self.broadcast(
#             Message(
#                 type=MessageType.TOOL_START,
#                 payload={
#                     "tool_name": tool_name,
#                     "stream_id": stream_id,
#                     "event_data": event,
#                 },
#             )
#         )

#     async def _handle_tool_end(self, stream_id: str, event: dict):
#         """Handle tool execution completion"""
#         tool_name = event["name"]
#         tool_output = event["data"].get("output")

#         await self.broadcast(
#             Message(
#                 type=MessageType.TOOL_END,
#                 payload={
#                     "tool_name": tool_name,
#                     "stream_id": stream_id,
#                     "tool_output": tool_output,
#                     "event_data": event,
#                 },
#             )
#         )

#     def _extract_text_content(self, chunk) -> str:
#         """Extract text content from LLM chunk"""
#         if hasattr(chunk, "content"):
#             if isinstance(chunk.content, str):
#                 return chunk.content
#             elif isinstance(chunk.content, list):
#                 text_parts = []
#                 for item in chunk.content:
#                     if isinstance(item, dict):
#                         if item.get("type") == "text" and "text" in item:
#                             text_parts.append(item["text"])
#                         elif "text" in item and item.get("type") != "input_json_delta":
#                             text_parts.append(item["text"])
#                     elif isinstance(item, str):
#                         text_parts.append(item)
#                 return "".join(text_parts)
#         return ""

#     async def subscriptions(self):
#         return [
#             MessageType.SHUTDOWN,
#             MessageType.USER_INPUT,
#             MessageType.AGENT_REQUEST,
#             MessageType.CANCEL_STREAM,
#         ]
