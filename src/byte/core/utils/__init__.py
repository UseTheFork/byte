"""Utilities."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.core.utils.dump import dd, dump
    from byte.core.utils.extract_content_from_message import extract_content_from_message
    from byte.core.utils.get_language_from_filename import get_language_from_filename
    from byte.core.utils.get_last_message import get_last_message
    from byte.core.utils.list_to_multiline_text import list_to_multiline_text
    from byte.core.utils.slugify import slugify
    from byte.core.utils.value import value

__all__ = (
    "dd",
    "dump",
    "extract_content_from_message",
    "get_language_from_filename",
    "get_last_message",
    "list_to_multiline_text",
    "slugify",
    "value",
)

_dynamic_imports = {
    "dd": "dump",
    "dump": "dump",
    "extract_content_from_message": "extract_content_from_message",
    "get_language_from_filename": "get_language_from_filename",
    "get_last_message": "get_last_message",
    "list_to_multiline_text": "list_to_multiline_text",
    "slugify": "slugify",
    "value": "value",
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
