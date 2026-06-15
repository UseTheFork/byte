"""Generate gateway-requests.md documentation from registered gateway request classes.

This script inspects the Requests namespace in src/byte/gateway/requests.py,
extracts request metadata, and generates formatted markdown documentation.

Usage: `uv run python src/scripts/requests_to_md.py`
"""

import dataclasses
import inspect
from pathlib import Path
from typing import Any, get_args

from byte.gateway.requests import GatewayRequest, Requests
from byte.support import Str


def get_request_classes() -> dict[str, type[GatewayRequest]]:
    """Discover all GatewayRequest subclasses from the Requests namespace.

    Returns a dictionary mapping snake_case method names to request classes.
    """
    request_classes: dict[str, type[GatewayRequest]] = {}

    for _, cls in inspect.getmembers(Requests, inspect.isclass):
        if issubclass(cls, GatewayRequest) and cls is not GatewayRequest:
            method_name = Str.class_to_snake_case(cls.__name__)
            request_classes[method_name] = cls

    return dict(sorted(request_classes.items()))


def format_field_type(field_type: Any) -> tuple[str, bool]:
    """Format a field type annotation into a readable type string and required status.

    Returns a tuple of (type_string, is_optional).
    """
    args = get_args(field_type)

    # Handle Union types (including Optional which is Union[T, None])
    if args and type(None) in args:
        non_none_types = [arg for arg in args if arg is not type(None)]
        is_optional = True
        if non_none_types:
            inner_type = non_none_types[0]
            if inner_type is str:
                return ("string", is_optional)
            elif inner_type is int:
                return ("integer", is_optional)
            elif inner_type is bool:
                return ("boolean", is_optional)
            elif inner_type is float:
                return ("number", is_optional)
            else:
                return (getattr(inner_type, "__name__", str(inner_type)), is_optional)
        return ("unknown", is_optional)

    # Handle direct types
    if field_type is str:
        return ("string", False)
    elif field_type is int:
        return ("integer", False)
    elif field_type is bool:
        return ("boolean", False)
    elif field_type is float:
        return ("number", False)
    else:
        return (str(field_type), False)


def get_field_description(field_name: str, field_type: Any) -> str:
    """Provide a description for a field based on its name and type.

    Returns a descriptive string suitable for markdown documentation.
    """
    descriptions: dict[str, str] = {
        "file_path": "Relative or absolute path to the file",
        "model": "The LLM model to use",
        "context_limit": "Maximum context length",
    }

    if field_name in descriptions:
        return descriptions[field_name]

    # Generate a default description from field name
    readable_name = field_name.replace("_", " ")
    return f"The {readable_name}"


def create_request_markdown(method_name: str, request_class: type[GatewayRequest]) -> str:
    """Generate markdown documentation for a single gateway request.

    Includes request heading, method name, parameters, response, and errors sections.
    """
    lines = []

    # Heading
    lines.append(f"### {method_name}")
    lines.append("")

    # Description from docstring
    description = (request_class.__doc__ or "").strip()
    if description:
        lines.append(description)
    else:
        lines.append("No description available")
    lines.append("")

    # Method name
    lines.append(f"**Method name**: `{method_name}`")
    lines.append("")

    # Parameters section
    lines.append("**Parameters**:")
    lines.append("")

    fields = dataclasses.fields(request_class)
    has_params = False

    for field in fields:
        if field.name == "id":
            continue

        has_params = True
        type_str, is_optional = format_field_type(field.type)
        required_str = "optional" if is_optional else "required"
        description = get_field_description(field.name, field.type)

        lines.append(f"- `{field.name}` ({type_str}, {required_str}) — {description}")

    if not has_params:
        lines.append("None")

    lines.append("")

    # Response section
    lines.append('**Response**: `{"ok": true}`')
    lines.append("")

    # Errors section
    lines.append("**Errors**: `-32001` (Internal Error) if operation fails")
    lines.append("")

    return "\n".join(lines)


def generate_requests_md() -> str:
    """Generate markdown documentation for all gateway requests.

    Returns the complete markdown content ready to be written to file.
    """
    lines = []

    request_classes = get_request_classes()

    for method_name, request_class in request_classes.items():
        markdown = create_request_markdown(method_name, request_class)
        lines.append(markdown)

    return "\n".join(lines)


def main() -> None:
    """Generate gateway-requests.md from registered request classes."""
    markdown = generate_requests_md()

    # Write to docs/references/gateway-requests.md
    output_file = Path(__file__).parent.parent.parent / "docs" / "references" / "gateway-requests.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(markdown, encoding="utf-8")

    print(f"Gateway requests documentation written to {output_file}")


if __name__ == "__main__":
    main()
