from typing import List, Type

from byte.parsing.service.skill_parsing_service import SkillParsingService
from byte.support import Service, ServiceProvider


class ParsingServiceProvider(ServiceProvider):
    """Service provider for the parsing domain.

    Registers services for parsing and validating skill files.
    """

    def services(self) -> List[Type[Service]]:
        return [SkillParsingService]
