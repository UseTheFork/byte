from dataclasses import dataclass, field


@dataclass
class TokenCount:
    """Token usage counts for input and output."""

    input: int = 0
    output: int = 0


@dataclass
class ModelUsage:
    """Token usage tracking for a specific model."""

    context: int = 0
    total: TokenCount = field(default_factory=TokenCount)


@dataclass
class LastMessageUsage:
    """Token usage for the last message sent."""

    input: int = 0
    output: int = 0
    type: str = ""


@dataclass
class UsageAnalytics:
    """Complete analytics tracking for all models and sessions."""

    last: LastMessageUsage = field(default_factory=LastMessageUsage)
    main: ModelUsage = field(default_factory=ModelUsage)
    weak: ModelUsage = field(default_factory=ModelUsage)
