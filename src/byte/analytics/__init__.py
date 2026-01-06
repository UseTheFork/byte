"""Analytics domain for tracking token usage and agent performance."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.analytics.schemas import LastMessageUsage, ModelUsage, TokenCount, UsageAnalytics
    from byte.analytics.service.agent_analytics_service import AgentAnalyticsService
    from byte.analytics.service_provider import AnalyticsProvider


__all__ = (
    "AgentAnalyticsService",
    "AnalyticsProvider",
    "LastMessageUsage",
    "ModelUsage",
    "TokenCount",
    "UsageAnalytics",
)

_dynamic_imports = {
    # keep-sorted start
    "AgentAnalyticsService": "service.agent_analytics_service",
    "AnalyticsProvider": "service_provider",
    "LastMessageUsage": "schemas",
    "ModelUsage": "schemas",
    "TokenCount": "schemas",
    "UsageAnalytics": "schemas",
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
