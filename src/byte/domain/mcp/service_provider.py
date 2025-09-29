from typing import List, Type

from rich.console import Console

from byte.container import Container
from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.llm.service.llm_service import LLMService


class MCPServiceProvider(ServiceProvider):
    """ """

    def services(self) -> List[Type[Service]]:
        return [LLMService]

    async def register(self, container: Container):
        pass

    async def boot(self, container: "Container") -> None:
        """Boot LLM services and display configuration information.

        Shows user which models are active for transparency and debugging,
        helping users understand which AI capabilities are available.
        Usage: Called automatically during application startup
        """
        llm_service = await container.make(LLMService)
        console = await container.make(Console)

        # Display active model configuration for user awareness
        main_model = llm_service._service_config.main.model
        weak_model = llm_service._service_config.weak.model
        console.print(f"├─ [success]Main model:[/success] [info]{main_model}[/info]")
        console.print(f"├─ [success]Weak model:[/success] [info]{weak_model}[/info]")
