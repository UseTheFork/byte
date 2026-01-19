from langchain_core.language_models.fake_chat_models import GenericFakeChatModel


class FakeChatModel(GenericFakeChatModel):
    """Extended fake chat model that supports structured output."""

    def with_structured_output(self, schema=None, **kwargs):
        """Return self to support structured output chaining."""
        return self

    # def bind_tools(self, functions: list):
    #     return self
