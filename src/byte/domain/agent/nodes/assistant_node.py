from langchain_core.runnables import Runnable
from langgraph.runtime import Runtime
from langgraph.types import Command

from byte.core.event_bus import EventType, Payload
from byte.core.logging import log
from byte.domain.agent.nodes.base_node import Node
from byte.domain.agent.schemas import AssistantContextSchema


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

	async def __call__(self, state, config, runtime: Runtime[AssistantContextSchema]):
		while True:
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

			template = runnable.get_prompts(config)
			prompt_value = await template[0].ainvoke(state)
			log.info(prompt_value)

			result = await runnable.ainvoke(state, config=config)

			# Ensure we get a real response
			if not result.tool_calls and (
				not result.content or (isinstance(result.content, list) and not result.content[0].get("text"))
			):
				# Re-prompt for actual response
				messages = state["messages"] + [("user", "Respond with a real output.")]
				state = {**state, "messages": messages}
			elif result.tool_calls and len(result.tool_calls) > 0:
				return Command(goto="tools_node", update={"messages": [result]})
			else:
				break

			await self.emit(payload)

		return Command(goto="end_node", update={"messages": [result]})
