from typing import Optional

from byte.core.array_store import ArrayStore
from byte.core.event_bus import Payload
from byte.core.service.base_service import Service
from byte.core.utils.list_to_multiline_text import list_to_multiline_text
from byte.domain.knowledge.models import SessionContextModel
from byte.domain.prompt_format.schemas import BoundaryType
from byte.domain.prompt_format.utils import Boundary


class SessionContextService(Service):
    """Service for managing session-specific context and documentation.

    Houses various documents or useful information that will be fed to the
    prompt via the add_session_context_hook. Uses ArrayStore for flexible
    key-value storage of context items.
    Usage: `await service.add_context("conventions", "Style guide content")`
    """

    async def boot(self):
        """Initialize the session context service with an empty store.

        Usage: `service = SessionContextService(container)`
        """
        self.session_context = ArrayStore()

    def add_context(self, model: SessionContextModel) -> "SessionContextService":
        """Add a context item to the session store.

        Usage: `service.add_context(SessionContextModel(type="file", key="style_guide", content="Follow PEP 8..."))`
        """
        self.session_context.add(model.key, model)
        return self

    def remove_context(self, key: str) -> "SessionContextService":
        """Remove a context item from the session store.

        Usage: `service.remove_context("old_convention")`
        """
        model = self.session_context.get(key)
        if model:
            model.delete()
        self.session_context.remove(key)
        return self

    def get_context(self, key: str) -> Optional[SessionContextModel]:
        """Retrieve a specific context item from the store.

        Usage: `model = service.get_context("style_guide")`
        """
        return self.session_context.get(key, None)

    def clear_context(self) -> "SessionContextService":
        """Clear all context items from the session store.

        Usage: `service.clear_context()`
        """
        for _, model in self.session_context.all().items():
            model.delete()
        self.session_context.set({})
        return self

    def get_all_context(self) -> dict[str, SessionContextModel]:
        """Retrieve all context items from the session store.

        Usage: `all_context = service.get_all_context()`
        """
        return self.session_context.all()

    async def add_session_context_hook(self, payload: Payload) -> Payload:
        """Inject session context into the prompt state.

        Aggregates all stored context items and adds them to the
        session_docs list for inclusion in the prompt.
        Usage: `result = await service.add_session_context_hook(payload)`
        """
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
            session_docs_list = payload.get("session_docs", [])
            session_docs_list.extend(formatted_contexts)
            payload.set("session_docs", session_docs_list)

        return payload
