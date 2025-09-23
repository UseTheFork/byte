import asyncio

from byte.core.actors.base import Actor
from byte.core.actors.message import (
    CompletionResponse,
    ExecuteCommand,
    GetCompletions,
    Message,
    MessageType,
)
from byte.domain.lint.service.lint_service import LintService


class LintActor(Actor):
    async def handle_message(self, message: Message):
        if isinstance(message, ExecuteCommand):
            await self._handle_lint_command(message)
        elif isinstance(message, GetCompletions):
            await self._handle_completions(message)
        elif message.type == MessageType.LINT_CHANGED_FILES:
            await self._handle_lint_command(message)

    async def _handle_lint_command(self, message: Message):
        """Handle /lint command from user input"""
        from byte.domain.git.actor.git_actor import GitActor

        try:
            stage_response_queue = asyncio.Queue()
            await self.send_to(
                GitActor,
                Message(
                    type=MessageType.GIT_STAGE_CHANGES,
                    payload={},
                    reply_to=stage_response_queue,
                ),
            )

            # Wait for staging to complete
            await stage_response_queue.get()

            lint_service = await self.make(LintService)
            results = await lint_service.lint_changed_files()

            # Reply with success if someone is waiting
            if message.reply_to:
                await self.reply(message, {"success": True, "results": results})

        except Exception as e:
            if message.reply_to:
                await self.reply(message, {"success": False, "error": str(e)})

    async def _handle_completions(self, message: GetCompletions):
        """Handle tab completion requests for lint command"""
        # For now, lint doesn't need file completions since it works on changed files
        # But you could add options like --all, --fix, etc.
        completions = []

        if message.reply_to:
            await message.reply_to.put(CompletionResponse(completions))

    async def subscriptions(self):
        return [
            MessageType.DOMAIN_COMMAND,
            MessageType.LINT_CHANGED_FILES,
        ]
