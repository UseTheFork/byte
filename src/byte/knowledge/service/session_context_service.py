from typing import Optional

from byte import Service
from byte.knowledge import SessionContextModel
from byte.orchestration import OrchestrationEvents
from byte.support import ArrayStore, Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text
from byte.tui import Messages


class SessionContextService(Service):
    """Manage session-specific context and documentation."""

    def boot(self) -> None:
        """Initialize the session context service with an empty store."""
        self.session_context = ArrayStore()

    def notify_context_stats(self) -> None:
        """Notify the system that a context file was added or removed."""

        self.emit_tui(
            Messages.UpdateContext(
                len(self.session_context.all().keys()),
            ),
        )

    def add_context(self, model: SessionContextModel) -> SessionContextService:
        """Add a context item to the session store."""
        self.session_context.add(model.key, model)
        self.notify_context_stats()
        return self

    def remove_context(self, key: str) -> SessionContextService:
        """Remove a context item from the session store."""
        model = self.session_context.get(key)
        if model:
            model.delete()
        self.session_context.remove(key)
        self.notify_context_stats()
        return self

    def get_context(self, key: str) -> Optional[SessionContextModel]:
        """Retrieve a specific context item from the store."""
        return self.session_context.get(key, None)

    def clear_context(self) -> SessionContextService:
        """Clear all context items from the session store."""
        for _, model in self.session_context.all().items():
            model.delete()
        self.session_context.set({})
        self.notify_context_stats()
        return self

    def get_all_context(self) -> dict[str, SessionContextModel]:
        """Retrieve all context items from the session store."""
        return self.session_context.all()

    async def add_session_context_hook(
        self, payload: OrchestrationEvents.GatherProjectContext
    ) -> OrchestrationEvents.GatherProjectContext:
        """Inject session context items into the prompt state."""
        if self.session_context.is_not_empty():
            # Format each context item with its own tags
            formatted_contexts = []
            for key, model in self.session_context.all().items():
                formatted_contexts.append(
                    list_to_multiline_text(
                        [
                            Boundary.open(
                                BoundaryType.SESSION_CONTEXT,
                                meta={"type": model.type, "key": key},
                            ),
                            model.content,
                            Boundary.close(BoundaryType.SESSION_CONTEXT),
                        ]
                    )
                )

            # Get existing list and extend with formatted contexts
            payload.session_docs.extend(formatted_contexts)

        return payload
