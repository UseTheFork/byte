# TODO: DOc String
""""""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.development.service.record_response_service import RecordResponseService
    from byte.development.service_provider import DevelopmentServiceProvider

__all__ = (
    "DevelopmentServiceProvider",
    "RecordResponseService",
)

_dynamic_imports = {
    # keep-sorted start
    "DevelopmentServiceProvider": "service_provider",
    "RecordResponseService": "service.record_response_service",
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
