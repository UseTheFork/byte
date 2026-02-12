"""Parsing domain for skill file parsing and validation."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.parsing.exceptions import ParseError, ValidationError
    from byte.parsing.schemas import ConventionProperties, ReferenceProperties, SkillProperties
    from byte.parsing.service.convention_parsing_service import ConventionParsingService
    from byte.parsing.service.parsing_service import ParsingService
    from byte.parsing.service.skill_parsing_service import SkillParsingService
    from byte.parsing.service_provider import ParsingServiceProvider
    from byte.parsing.validators.convention_validator import ConventionValidator
    from byte.parsing.validators.skill_validator import SkillValidator

__all__ = (
    "ConventionParsingService",
    "ConventionProperties",
    "ConventionValidator",
    "ParseError",
    "ParsingService",
    "ParsingServiceProvider",
    "ReferenceProperties",
    "SkillParsingService",
    "SkillProperties",
    "SkillValidator",
    "ValidationError",
)

_dynamic_imports = {
    # keep-sorted start
    "ConventionParsingService": "service.convention_parsing_service",
    "ConventionProperties": "schemas",
    "ConventionValidator": "validators.convention_validator",
    "ParseError": "exceptions",
    "ParsingService": "service.parsing_service",
    "ParsingServiceProvider": "service_provider",
    "ReferenceProperties": "schemas",
    "SkillParsingService": "service.skill_parsing_service",
    "SkillProperties": "schemas",
    "SkillValidator": "validators.skill_validator",
    "ValidationError": "exceptions",
    # keep-sorted end
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
