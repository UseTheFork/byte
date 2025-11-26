import asyncio

from byte.core.mixins.bootable import Bootable


class TaskManager(Bootable):
    async def boot(self):
        self._tasks = {}

    def start_task(self, name: str, coro):
        """Start a named background task"""
        if name in self._tasks:
            self._tasks[name].cancel()

        self._tasks[name] = asyncio.create_task(coro)
        return self._tasks[name]

    def stop_task(self, name: str):
        """Stop a named task"""
        if name in self._tasks:
            self._tasks[name].cancel()
            del self._tasks[name]

    async def shutdown(self):
        """Stop all tasks"""
        for task in self._tasks.values():
            task.cancel()
        await asyncio.gather(*self._tasks.values(), return_exceptions=True)
