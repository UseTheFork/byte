from byte.agent import BaseState, ValidationError
from byte.agent.validators.base import Validator
from byte.support.mixins import UserInteractive
from byte.support.utils import get_last_message


class UserConfirmValidator(Validator, UserInteractive):
    """ """

    async def validate(self, state: BaseState) -> list[ValidationError | None]:
        content = get_last_message(state["scratch_messages"])

        self.app["console"].print_warning_panel(
            content,
            title="Proposed Content",
        )

        confirmed, change = await self.prompt_for_confirm_or_input("Approve?", "What should be changed?", True)

        if confirmed:
            return [None]

        return [ValidationError(context=content, message=str(change))]
