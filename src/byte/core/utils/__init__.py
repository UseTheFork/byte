import inspect
import sys
from collections.abc import Callable

from rich.pretty import pprint


def dump(*args, **kwargs):
	"""Debug function that pretty prints variables using rich.

	Usage:
	dump(variable1, variable2)
	dump(locals())
	dump(globals())
	"""
	# Get caller information
	frame = inspect.currentframe().f_back
	filename = frame.f_code.co_filename
	lineno = frame.f_lineno

	# Print location information
	print(f"[dim]Debug output from {filename}:{lineno}[/dim]")

	if not args and not kwargs:
		# If no arguments, dump the caller's locals
		pprint(frame.f_locals)
	else:
		# Print each argument
		for arg in args:
			pprint(arg)

		# Print keyword arguments
		if kwargs:
			pprint(kwargs)


def dd(*args, **kwargs):
	"""Debug function that dumps variables and then exits.

	Usage:
	dd(variable1, variable2)  # Prints variables and exits
	dd(locals())  # Prints local scope and exits
	"""
	dump(*args, **kwargs)
	sys.exit(1)


def get_last_message(state):
	"""Extract the last message from a state dict or list.

	Handles both list-based states and dict-based states with a "messages" key.
	Raises ValueError if no messages are found.

	Usage: `last_msg = get_last_message(state)` -> most recent message
	"""
	if isinstance(state, list):
		if not state:
			raise ValueError("No messages found in empty list state")
		return state[-1]
	elif messages := state.get("messages", []):
		return messages[-1]
	else:
		raise ValueError(f"No messages found in input state: {state}")


def extract_content_from_message(message) -> str:
	"""Extract text content from message chunks with format-aware processing.

	Handles both string content and list-based content formats from different
	LLM providers, ensuring consistent text extraction across message types.
	Usage: `content = self._extract_content(chunk)` -> extracted text string
	"""
	if isinstance(message.content, str):
		return message.content
	elif isinstance(message.content, list) and message.content:
		return message.content[0].get("text", "")

	raise ValueError(f"Unable to extract content from message: {type(message.content)}")


def value(val, *args, **kwargs):
	"""Return the default value of the given value.

	If the value is callable, invoke it with the provided arguments.
	Otherwise, return the value as-is.
	Usage: `result = value(lambda: expensive_operation())` or `result = value(42)`
	"""

	return val(*args, **kwargs) if isinstance(val, Callable) else val


def slugify(text: str) -> str:
	"""Convert a string to a URL-safe slug format.

	Converts text to lowercase, replaces non-alphanumeric characters with
	hyphens, and removes leading/trailing hyphens. Useful for creating
	keys from URLs or arbitrary text.
	Usage: `key = slugify("https://example.com/page")` -> "https-example-com-page"
	"""
	import re

	# Convert to lowercase
	text = text.lower()
	# Replace non-alphanumeric characters with hyphens
	text = re.sub(r"[^a-z0-9]+", "-", text)
	# Remove leading/trailing hyphens
	text = text.strip("-")
	return text
