from byte.agent import BaseState, ValidationError
from byte.agent.validators.base import Validator
from byte.parsing import (
    ConventionParsingService,
    ParseError,
    ValidationError as ConventionValidationError,
)
from byte.support.mixins import UserInteractive
from byte.support.utils import extract_content_from_message, get_last_message


class ConventionValidator(Validator, UserInteractive):
    """Validator for skill SKILL.md content with metadata validation.

    Validates skill content by parsing YAML frontmatter and checking that
    required fields (name, description) are present and properly formatted.
    Returns ValidationError with specific issues if validation fails.

    Usage: `validator = app.make(SkillValidator)`
    Usage: `errors = await validator.validate(state)`
    """

    async def validate(self, state: BaseState) -> list[ValidationError | None]:
        last_message = get_last_message(state["scratch_messages"])
        message_content = extract_content_from_message(last_message)

        skill_parsing_service = self.app.make(ConventionParsingService)

        try:
            metadata, _ = skill_parsing_service.parse_frontmatter(message_content)
        except ParseError as e:
            return [ValidationError(message=str(e))]
        except ConventionValidationError as e:
            return [ValidationError(message=str(e))]

        validation_errors = []

        validation_errors.extend(skill_parsing_service.validate_metadata_fields(metadata))

        if "name" in metadata:
            validation_errors.extend(skill_parsing_service.validate_name(metadata["name"]))

        if "description" in metadata:
            validation_errors.extend(skill_parsing_service.validate_description(metadata["description"]))

        if validation_errors:
            error_message = "\n".join(f"- {error}" for error in validation_errors)
            return [ValidationError(message=error_message)]

        return []
