from typing import List, Type

from byte import Service, ServiceProvider
from byte.constitution.service.constitution_service import ConstitutionService


class ConstitutionServiceProvider(ServiceProvider):
    """Service provider for the constitution domain.

    Registers and boots the ConstitutionService, which loads the project
    constitution from ``.byte/constitution.json`` on startup.
    """

    def services(self) -> List[Type[Service]]:
        return [ConstitutionService]

    async def boot(self) -> None:
        """Boot the constitution service."""
        self.app.make(ConstitutionService)

