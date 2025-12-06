from byte.domain.web.parser.base import BaseWebParser
from byte.domain.web.parser.generic_parser import GenericParser
from byte.domain.web.parser.gitbook_parser import GitBookParser
from byte.domain.web.parser.github_parser import GitHubParser
from byte.domain.web.parser.mkdocs_parser import MkDocsParser
from byte.domain.web.parser.raw_content_parser import RawContentParser
from byte.domain.web.parser.readthedocs_parser import ReadTheDocsParser

__all__ = [
    "BaseWebParser",
    "GenericParser",
    "GitBookParser",
    "GitHubParser",
    "MkDocsParser",
    "RawContentParser",
    "ReadTheDocsParser",
]
