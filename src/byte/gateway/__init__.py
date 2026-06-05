"""Gateway domain for WebSocket JSON-RPC bridge."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.gateway.config import GatewayConfig
    from byte.gateway.service.gateway_service import GatewayService
    from byte.gateway.service.session_service import SessionService
    from byte.gateway.service_provider import GatewayServiceProvider

__all__ = (
    "GatewayConfig",
    "GatewayService",
    "GatewayServiceProvider",
    "SessionService",
)

_dynamic_imports = {
    # keep-sorted start
    "GatewayConfig": "config",
    "GatewayService": "service.gateway_service",
    "GatewayServiceProvider": "service_provider",
    "SessionService": "service.session_service",
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
