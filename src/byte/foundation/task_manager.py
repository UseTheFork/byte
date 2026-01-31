import asyncio

from byte.support.mixins.bootable import Bootable


class TaskManager(Bootable):
    def __init__(self, *args, **kwargs):
        self._tasks = {}

    def _handle_task_exception(self, task, name):
        """Handle exceptions from background tasks"""
        try:
            task.result()
        except asyncio.CancelledError:
            pass  # Expected when shutting down
        except Exception as e:
            print(f"Task {name} failed: {e}")  # Or use proper logging

    def start_task(self, name: str, coro):
        """Start a named background task"""
        import asyncio

        if name in self._tasks:
            self._tasks[name].cancel()

        task = asyncio.create_task(coro)
        task.add_done_callback(lambda t: self._handle_task_exception(t, name))
        self._tasks[name] = task
        return task

    def stop_task(self, name: str):
        """Stop a named task"""
        if name in self._tasks:
            self._tasks[name].cancel()
            del self._tasks[name]

    def dispatch_task(self, coro):
        """Dispatch a fire-and-forget background task with auto-generated name"""
        import uuid

        name = f"task_{uuid.uuid4().hex[:8]}"
        return self.start_task(name, coro)

    async def shutdown(self):
        """Stop all tasks"""
        for task in self._tasks.values():
            task.cancel()
        await asyncio.gather(*self._tasks.values(), return_exceptions=True)
