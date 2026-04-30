"""LSP domain for Language Server Protocol integration."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.lsp.config import (
        ContainerServerConfig,
        CustomServerConfig,
        LocalServerConfig,
        LSPConfig,
        PresetServerConfig,
    )
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
    from byte.lsp.tools.find_references import FindReferencesTool
    from byte.lsp.tools.get_definition import GetDefinitionTool
    from byte.lsp.tools.get_hover_info import GetHoverInfoTool


__all__ = (
    "CompletionItem",
    "ContainerServerConfig",
    "CustomServerConfig",
    "Diagnostic",
    "DiagnosticSeverity",
    "FindReferencesTool",
    "GetDefinitionTool",
    "GetHoverInfoTool",
    "HoverResult",
    "LSPClient",
    "LSPConfig",
    "LSPServerConfig",
    "LSPService",
    "LSPServiceProvider",
    "LocalServerConfig",
    "Location",
    "LspServerState",
    "Position",
    "PresetServerConfig",
    "Range",
    "TextDocumentIdentifier",
)

_dynamic_imports = {
    # keep-sorted start
    "CompletionItem": "schemas",
    "ContainerServerConfig": "config",
    "CustomServerConfig": "config",
    "Diagnostic": "schemas",
    "DiagnosticSeverity": "schemas",
    "FindReferencesTool": "tools.find_references",
    "GetDefinitionTool": "tools.get_definition",
    "GetHoverInfoTool": "tools.get_hover_info",
    "HoverResult": "schemas",
    "LSPClient": "service.lsp_client",
    "LSPConfig": "config",
    "LSPServerConfig": "config",
    "LSPService": "service.lsp_service",
    "LSPServiceProvider": "service_provider",
    "LocalServerConfig": "config",
    "Location": "schemas",
    "LspServerState": "schemas",
    "Position": "schemas",
    "PresetServerConfig": "config",
    "Range": "schemas",
    "TextDocumentIdentifier": "schemas",
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
