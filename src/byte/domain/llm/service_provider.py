from typing import List, Type

from byte.container import Container
from byte.core.event_bus import EventBus, EventType
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli.service.console_service import ConsoleService
from byte.domain.llm.service.llm_service import LLMService


class LLMServiceProvider(ServiceProvider):
	"""Service provider for LLM functionality.

	Automatically detects and configures the best available LLM provider
	based on environment variables and API key availability. Supports
	provider preference via BYTE_LLM_PROVIDER environment variable.
	Usage: Register with container to enable AI functionality throughout app
	"""

	def services(self) -> List[Type[Service]]:
		return [LLMService]

	async def boot(self, container: "Container") -> None:
		"""Boot LLM services and display configuration information.

		Shows user which models are active for transparency and debugging,
		helping users understand which AI capabilities are available.
		Usage: Called automatically during application startup
		"""
		event_bus = await container.make(EventBus)
		llm_service = await container.make(LLMService)
		console = await container.make(ConsoleService)

		# Display active model configuration for user awareness
		main_model = llm_service._service_config.main.params.model
		weak_model = llm_service._service_config.weak.params.model
		console.print(f"│ [success]Main model:[/success] [info]{main_model}[/info]")
		console.print(f"│ [success]Weak model:[/success] [info]{weak_model}[/info]")

		# Register listener that calls list_in_context_files before each prompt
		event_bus.on(
			EventType.GATHER_REINFORCEMENT.value,
			llm_service.add_reinforcement_hook,
		)
