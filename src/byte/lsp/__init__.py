"""LSP domain for Language Server Protocol integration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.lsp.config import LSPConfig, LSPServerConfig
    from byte.lsp.schemas import (
        CompletionItem,
        Diagnostic,
        DiagnosticSeverity,
        HoverResult,
        Location,
        LspServerState,
        Position,
        Range,
        TextDocumentIdentifier,
    )
    from byte.lsp.service.lsp_client import LSPClient
    from byte.lsp.service.lsp_service import LSPService
    from byte.lsp.service_provider import LSPServiceProvider
    from byte.lsp.tools.find_references import find_references
    from byte.lsp.tools.get_definition import get_definition
    from byte.lsp.tools.get_hover_info import get_hover_info

__all__ = (
    "CompletionItem",
    "Diagnostic",
    "DiagnosticSeverity",
    "HoverResult",
    "LSPClient",
    "LSPConfig",
    "LSPServerConfig",
    "LSPService",
    "LSPServiceProvider",
    "Location",
    "LspServerState",
    "Position",
    "Range",
    "TextDocumentIdentifier",
    "find_references",
    "get_definition",
    "get_hover_info",
)

_dynamic_imports = {
    # keep-sorted start
    "CompletionItem": "schemas",
    "Diagnostic": "schemas",
    "DiagnosticSeverity": "schemas",
    "HoverResult": "schemas",
    "LSPClient": "service.lsp_client",
    "LSPConfig": "config",
    "LSPServerConfig": "config",
    "LSPService": "service.lsp_service",
    "LSPServiceProvider": "service_provider",
    "Location": "schemas",
    "LspServerState": "schemas",
    "Position": "schemas",
    "Range": "schemas",
    "TextDocumentIdentifier": "schemas",
    "find_references": "tools.find_references",
    "get_definition": "tools.get_definition",
    "get_hover_info": "tools.get_hover_info",
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
