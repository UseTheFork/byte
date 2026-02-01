"""Utilities."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.support.utils.dump import dd, dump
    from byte.support.utils.extract_content_from_message import extract_content_from_message
    from byte.support.utils.extract_json_from_message import extract_json_from_message
    from byte.support.utils.get_language_from_filename import get_language_from_filename
    from byte.support.utils.get_last_ai_message import get_last_ai_message
    from byte.support.utils.get_last_message import get_last_message
    from byte.support.utils.list_to_multiline_text import list_to_multiline_text
    from byte.support.utils.parse_partial_json import parse_partial_json
    from byte.support.utils.slugify import slugify
    from byte.support.utils.value import value

__all__ = (
    "dd",
    "dump",
    "extract_content_from_message",
    "extract_json_from_message",
    "get_language_from_filename",
    "get_last_ai_message",
    "get_last_message",
    "list_to_multiline_text",
    "parse_partial_json",
    "slugify",
    "value",
)

_dynamic_imports = {
    # keep-sorted start
    "dd": "dump",
    "dump": "dump",
    "extract_content_from_message": "extract_content_from_message",
    "extract_json_from_message": "extract_json_from_message",
    "get_language_from_filename": "get_language_from_filename",
    "get_last_ai_message": "get_last_ai_message",
    "get_last_message": "get_last_message",
    "list_to_multiline_text": "list_to_multiline_text",
    "parse_partial_json": "parse_partial_json",
    "slugify": "slugify",
    "value": "value",
    # keep-sorted end
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
