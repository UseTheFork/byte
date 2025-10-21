from byte.domain.agent.schemas import TokenUsageSchema


def replace_list(left: list | None, right: list) -> list:
	"""Reducer that replaces the entire list with new values.

	Unlike the default add_messages which appends, this replaces the full list.
	Used with Annotated to handle state updates that should completely replace
	rather than accumulate values.

	Usage: `errors: Annotated[list[AnyMessage], replace_list]`
	"""
	return right


def add_token_usage(left: TokenUsageSchema | None, right: TokenUsageSchema) -> TokenUsageSchema:
	"""Reducer that accumulates token usage by adding counts together.

	Combines input_tokens, output_tokens, and total_tokens from both schemas.
	Used with Annotated to track cumulative token usage across multiple LLM calls.

	Usage: `llm_main_usage: Annotated[TokenUsageSchema, add_token_usage]`
	"""
	if left is None:
		return right

	return TokenUsageSchema(
		input_tokens=left.input_tokens + right.input_tokens,
		output_tokens=left.output_tokens + right.output_tokens,
		total_tokens=left.total_tokens + right.total_tokens,
	)
