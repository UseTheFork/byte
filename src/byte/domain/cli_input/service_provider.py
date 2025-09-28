from typing import List, Type

from byte.core.service.base_service import Service
from byte.core.service_provider import ServiceProvider
from byte.domain.cli_input.service.interactions_service import InteractionService
from byte.domain.cli_input.service.prompt_toolkit_service import PromptToolkitService


class CliInputServiceProvider(ServiceProvider):
    """Service provider for UI system."""

    def services(self) -> List[Type[Service]]:
        return [InteractionService, PromptToolkitService]
