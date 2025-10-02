from typing import TYPE_CHECKING

from byte.core.service_provider import ServiceProvider
from byte.domain.edit_format.service.edit_format_service import EditFormatService

if TYPE_CHECKING:
    from byte.container import Container


class EditFormatProvider(ServiceProvider):
    """ """

    async def register(self, container: "Container"):
        """ """
        container.bind(EditFormatService)
