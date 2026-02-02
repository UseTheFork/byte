"""Web domain for browser automation and web scraping."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.web.config import WebConfig
    from byte.web.exceptions import WebNotEnabledException
    from byte.web.parser.base import BaseWebParser
    from byte.web.parser.generic_parser import GenericParser
    from byte.web.parser.gitbook_parser import GitBookParser
    from byte.web.parser.github_parser import GitHubParser
    from byte.web.parser.mkdocs_parser import MkDocsParser
    from byte.web.parser.raw_content_parser import RawContentParser
    from byte.web.parser.sphinx_parser import SphinxParser
    from byte.web.service.chromium_service import ChromiumService
    from byte.web.service.content_cleaner import ContentCleaner
    from byte.web.service_provider import WebServiceProvider

__all__ = (
    "BaseWebParser",
    "ChromiumService",
    "ContentCleaner",
    "GenericParser",
    "GitBookParser",
    "GitHubParser",
    "MkDocsParser",
    "RawContentParser",
    "SphinxParser",
    "WebConfig",
    "WebNotEnabledException",
    "WebServiceProvider",
)

_dynamic_imports = {
    # keep-sorted start
    "BaseWebParser": "parser.base",
    "ChromiumService": "service.chromium_service",
    "ContentCleaner": "service.content_cleaner",
    "GenericParser": "parser.generic_parser",
    "GitBookParser": "parser.gitbook_parser",
    "GitHubParser": "parser.github_parser",
    "MkDocsParser": "parser.mkdocs_parser",
    "RawContentParser": "parser.raw_content_parser",
    "SphinxParser": "parser.sphinx_parser",
    "WebConfig": "config",
    "WebNotEnabledException": "exceptions",
    "WebServiceProvider": "service_provider",
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
