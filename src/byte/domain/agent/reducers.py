def replace_list(left: list | None, right: list) -> list:
	"""Reducer that replaces the entire list with new values.

	Unlike the default add_messages which appends, this replaces the full list.
	Used with Annotated to handle state updates that should completely replace
	rather than accumulate values.

	Usage: `errors: Annotated[list[AnyMessage], replace_list]`
	"""
	return right
