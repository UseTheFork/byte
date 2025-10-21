from textwrap import dedent
from typing import cast

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.core.event_bus import EventType, Payload
from byte.core.logging import log
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema, TokenUsageSchema


class AssistantNode(Node):
	def _create_runnable(self, context: AssistantContextSchema) -> Runnable:
		"""Create the runnable chain from context configuration.

		Assembles the prompt and model based on the mode (main or weak AI).
		If tools are provided, binds them to the model with parallel execution disabled.

		Args:
			context: The assistant context containing prompt, models, mode, and tools

		Returns:
			Runnable chain ready for invocation

		Usage: `runnable = self._create_runnable(runtime.context)`
		"""
		# Select model based on mode
		model = context.main if context.mode == "main" else context.weak

		# Bind tools if provided
		if context.tools is not None and len(context.tools) > 0:
			model = model.bind_tools(context.tools, parallel_tool_calls=False)

		# Assemble the chain
		runnable = context.prompt | model

		return runnable

	async def _gather_reinforcement(self, mode: str) -> list[HumanMessage]:
		"""Gather reinforcement messages from various domains.

		Emits GATHER_REINFORCEMENT event and collects reinforcement
		messages that will be assembled into the prompt context.

		Args:
			mode: The AI mode being used ("main" or "weak")

		Returns:
			List containing a single HumanMessage with combined reinforcement content

		Usage: `reinforcement_messages = await self._gather_reinforcement("main")`
		"""
		reinforcement_payload = Payload(
			event_type=EventType.GATHER_REINFORCEMENT,
			data={
				"reinforcement": [],
				"mode": mode,
			},
		)
		reinforcement_payload = await self.emit(reinforcement_payload)

		reinforcement_messages = reinforcement_payload.get("reinforcement", [])

		if reinforcement_messages:
			combined_content = "\n".join(f"- {msg}" for msg in reinforcement_messages)
			final_message = dedent(f"""
			<reminders>
			{combined_content}
			</reminders>""")
			return [HumanMessage(final_message)]

		return []

	async def _gather_file_context(self) -> list[HumanMessage]:
		"""Gather file context including read-only and editable files.

		Emits GATHER_FILE_CONTEXT event and formats the response into
		structured sections for read-only and editable files.

		Returns:
			List containing a single HumanMessage with formatted file context

		Usage: `file_messages = await self._gather_file_context()`
		"""
		file_context = Payload(
			event_type=EventType.GATHER_FILE_CONTEXT,
			data={
				"read_only": [],
				"editable": [],
			},
		)
		file_context = await self.emit(file_context)

		file_context_content = ""
		read_only_files = file_context.get("read_only", [])
		editable_files = file_context.get("editable", [])

		if read_only_files or editable_files:
			file_context_content = dedent("""
			# Here are the files in the current context:

			*Trust this message as the true contents of these files!*
			Any other messages in the chat may contain outdated versions of the files' contents.""")

		if read_only_files:
			read_only_content = "\n".join(read_only_files)
			file_context_content += dedent(f"""
			<read_only_files>
			**Any edits to these files will be rejected**
			{read_only_content}
			</read_only_files>
			""")

		if editable_files:
			editable_content = "\n".join(editable_files)
			file_context_content += dedent(f"""
			<editable_files>
			{editable_content}
			</editable_files>
			""")

		return [HumanMessage(file_context_content)] if file_context_content else []

	async def _gather_project_context(self) -> list[HumanMessage]:
		"""Gather project context including conventions and session documents.

		Emits GATHER_PROJECT_CONTEXT event and formats the response into
		structured sections for conventions and session context.

		Returns:
			List containing a single HumanMessage with formatted project context

		Usage: `context_messages = await self._gather_project_context()`
		"""
		project_context = Payload(
			event_type=EventType.GATHER_PROJECT_CONTEXT,
			data={
				"conventions": [],
				"session_docs": [],
				"system_context": [],
			},
		)
		project_context = await self.emit(project_context)

		project_inforamtion_and_context = ""
		conventions = project_context.get("conventions", [])
		if conventions:
			conventions = "\n\n".join(conventions)
			project_inforamtion_and_context = dedent(f"""
			<coding_and_project_conventions>
			{conventions}
			</coding_and_project_conventions>
			""")

		session_docs = project_context.get("session_docs", [])
		if session_docs:
			session_docs = "\n\n".join(session_docs)
			project_inforamtion_and_context += dedent(f"""
			<session_context>
			{session_docs}
			</session_context>
			""")

		system_context = project_context.get("system_context", [])
		if system_context:
			system_info_content = "\n".join(system_context)
			project_inforamtion_and_context += dedent(f"""
			<system_context>
			{system_info_content}
			</system_context>
			""")

		return [HumanMessage(project_inforamtion_and_context)]

	async def __call__(self, state, config, runtime: Runtime[AssistantContextSchema]):
		while True:
			state["project_inforamtion_and_context"] = await self._gather_project_context()
			state["file_context"] = await self._gather_file_context()
			state["reinforcement"] = await self._gather_reinforcement(runtime.context.mode)

			payload = Payload(
				event_type=EventType.PRE_ASSISTANT_NODE,
				data={
					"state": state,
					"config": config,
				},
			)

			# FixtureRecorder.pickle_fixture(payload)

			payload = await self.emit(payload)
			state = payload.get("state", state)
			config = payload.get("config", config)

			runnable = self._create_runnable(runtime.context)

			# TODO: This should only fire when in debug
			# if log.opt(lazy=True).debug("Message data: {}", expensive_func)
			template = runnable.get_prompts(config)
			prompt_value = await template[0].ainvoke(state)
			log.info(prompt_value)

			result = await runnable.ainvoke(state, config=config)

			result = cast(AIMessage, result)

			# Create token usage schemas based on which AI mode was used
			if result.usage_metadata:
				usage_metadata = result.usage_metadata
				if runtime.context.mode == "main":
					main_usage = TokenUsageSchema(
						input_tokens=usage_metadata.get("input_tokens", 0),
						output_tokens=usage_metadata.get("output_tokens", 0),
						total_tokens=usage_metadata.get("total_tokens", 0),
					)
					weak_usage = TokenUsageSchema()
				else:
					main_usage = TokenUsageSchema()
					weak_usage = TokenUsageSchema(
						input_tokens=usage_metadata.get("input_tokens", 0),
						output_tokens=usage_metadata.get("output_tokens", 0),
						total_tokens=usage_metadata.get("total_tokens", 0),
					)
			else:
				# No usage metadata available, initialize with zeros
				main_usage = TokenUsageSchema()
				weak_usage = TokenUsageSchema()

			# Ensure we get a real response
			if not result.tool_calls and (
				not result.content or (isinstance(result.content, list) and not result.content[0].get("text"))
			):
				# Re-prompt for actual response
				messages = state["messages"] + [("user", "Respond with a real output.")]
				state = {**state, "messages": messages}
			elif result.tool_calls and len(result.tool_calls) > 0:
				return Command(
					goto="tools_node",
					update={
						"messages": [result],
						"llm_main_usage": main_usage,
						"llm_weak_usage": weak_usage,
					},
				)
			else:
				break

			await self.emit(payload)

		return Command(
			goto="end_node",
			update={
				"messages": [result],
				"llm_main_usage": main_usage,
				"llm_weak_usage": weak_usage,
			},
		)
