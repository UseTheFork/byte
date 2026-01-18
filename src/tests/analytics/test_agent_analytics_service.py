from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from byte import EventType
from byte.agent import TokenUsageSchema
from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestAgentAnalyticsService(BaseTest):
    """Test suite for AgentAnalyticsService."""

    @pytest.fixture
    def providers(self):
        """Provide AnalyticsProvider for analytics service tests."""
        from byte.analytics import AnalyticsProvider

        return [AnalyticsProvider]

    @pytest.mark.asyncio
    async def test_boot_initializes_usage_analytics(self, application: Application):
        """Test that boot initializes UsageAnalytics instance."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        assert service.usage is not None
        assert service.usage.main.context == 0
        assert service.usage.main.total.input == 0
        assert service.usage.main.total.output == 0
        assert service.usage.weak.context == 0
        assert service.usage.weak.total.input == 0
        assert service.usage.weak.total.output == 0

    @pytest.mark.asyncio
    async def test_update_main_usage_updates_counters(self, application: Application):
        """Test that update_main_usage correctly updates main model usage counters."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        token_usage = TokenUsageSchema(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        )

        await service.update_main_usage(token_usage)

        assert service.usage.main.context == 150
        assert service.usage.main.total.input == 100
        assert service.usage.main.total.output == 50
        assert service.usage.last.input == 100
        assert service.usage.last.output == 50
        assert service.usage.last.type == "main"

    @pytest.mark.asyncio
    async def test_update_main_usage_accumulates_totals(self, application: Application):
        """Test that update_main_usage accumulates total usage across multiple calls."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        # First update
        token_usage1 = TokenUsageSchema(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        )
        await service.update_main_usage(token_usage1)

        # Second update
        token_usage2 = TokenUsageSchema(
            input_tokens=200,
            output_tokens=75,
            total_tokens=275,
        )
        await service.update_main_usage(token_usage2)

        assert service.usage.main.context == 275
        assert service.usage.main.total.input == 300
        assert service.usage.main.total.output == 125
        assert service.usage.last.input == 200
        assert service.usage.last.output == 75

    @pytest.mark.asyncio
    async def test_update_weak_usage_updates_counters(self, application: Application):
        """Test that update_weak_usage correctly updates weak model usage counters."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        token_usage = TokenUsageSchema(
            input_tokens=50,
            output_tokens=25,
            total_tokens=75,
        )

        await service.update_weak_usage(token_usage)

        assert service.usage.weak.total.input == 50
        assert service.usage.weak.total.output == 25
        assert service.usage.last.input == 50
        assert service.usage.last.output == 25
        assert service.usage.last.type == "weak"

    @pytest.mark.asyncio
    async def test_update_weak_usage_accumulates_totals(self, application: Application):
        """Test that update_weak_usage accumulates total usage across multiple calls."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        # First update
        token_usage1 = TokenUsageSchema(
            input_tokens=50,
            output_tokens=25,
            total_tokens=75,
        )
        await service.update_weak_usage(token_usage1)

        # Second update
        token_usage2 = TokenUsageSchema(
            input_tokens=100,
            output_tokens=40,
            total_tokens=140,
        )
        await service.update_weak_usage(token_usage2)

        assert service.usage.weak.total.input == 150
        assert service.usage.weak.total.output == 65
        assert service.usage.last.input == 100
        assert service.usage.last.output == 40

    @pytest.mark.asyncio
    async def test_reset_usage_clears_all_counters(self, application: Application):
        """Test that reset_usage clears all usage counters."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        # Set some usage
        token_usage = TokenUsageSchema(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        )
        await service.update_main_usage(token_usage)
        await service.update_weak_usage(token_usage)

        # Reset
        service.reset_usage()

        assert service.usage.main.context == 0
        assert service.usage.main.total.input == 0
        assert service.usage.main.total.output == 0
        assert service.usage.weak.context == 0
        assert service.usage.weak.total.input == 0
        assert service.usage.weak.total.output == 0
        assert service.usage.last.input == 0
        assert service.usage.last.output == 0

    @pytest.mark.asyncio
    async def test_reset_context_clears_context_only(self, application: Application):
        """Test that reset_context clears context counters but preserves totals."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        # Set some usage
        token_usage = TokenUsageSchema(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        )
        await service.update_main_usage(token_usage)

        # Reset context
        service.reset_context()

        assert service.usage.main.context == 0
        assert service.usage.weak.context == 0
        # Totals should be preserved
        assert service.usage.main.total.input == 100
        assert service.usage.main.total.output == 50

    @pytest.mark.asyncio
    async def test_humanizer_formats_small_numbers(self, application: Application):
        """Test that humanizer returns small numbers as-is."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        assert service.humanizer(0) == "0"
        assert service.humanizer(1) == "1"
        assert service.humanizer(999) == "999"

    @pytest.mark.asyncio
    async def test_humanizer_formats_thousands(self, application: Application):
        """Test that humanizer formats thousands with K suffix."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        assert service.humanizer(1000) == "1K"
        assert service.humanizer(1500) == "1.5K"
        assert service.humanizer(10000) == "10K"
        assert service.humanizer(999999) == "1000.0K"

    @pytest.mark.asyncio
    async def test_humanizer_formats_millions(self, application: Application):
        """Test that humanizer formats millions with M suffix."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        assert service.humanizer(1000000) == "1000K"
        assert service.humanizer(1500000) == "1.5M"
        assert service.humanizer(10000000) == "10M"
        assert service.humanizer(999999999) == "1000.0M"

    @pytest.mark.asyncio
    async def test_humanizer_formats_billions(self, application: Application):
        """Test that humanizer formats billions with B suffix."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        assert service.humanizer(1000000000) == "1000M"
        assert service.humanizer(1500000000) == "1.5B"
        assert service.humanizer(10000000000) == "10B"

    @pytest.mark.asyncio
    async def test_humanizer_formats_trillions(self, application: Application):
        """Test that humanizer formats trillions with T suffix."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        assert service.humanizer(1000000000000) == "1000B"
        assert service.humanizer(1500000000000) == "1.5T"

    @pytest.mark.asyncio
    async def test_humanizer_handles_floats(self, application: Application):
        """Test that humanizer handles float inputs correctly."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        assert service.humanizer(1234.5) == "1.2K"
        assert service.humanizer(1500000.7) == "1.5M"

    @pytest.mark.asyncio
    async def test_usage_panel_hook_returns_payload(self, application: Application):
        """Test that usage_panel_hook returns a Payload object."""
        from byte import Payload
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        payload = Payload(EventType.POST_PROMPT_TOOLKIT, data={"info_panel": []})
        result = await service.usage_panel_hook(payload)

        assert isinstance(result, Payload)
        assert "info_panel" in result.data._data

    @pytest.mark.asyncio
    async def test_usage_panel_hook_adds_panel_to_info_panel(self, application: Application):
        """Test that usage_panel_hook adds analytics panel to info_panel list."""
        from byte import Payload
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        payload = Payload(EventType.POST_PROMPT_TOOLKIT, data={"info_panel": []})
        result = await service.usage_panel_hook(payload)

        info_panel = result.get("info_panel", [])
        assert len(info_panel) == 1

    @pytest.mark.asyncio
    async def test_usage_panel_hook_preserves_existing_panels(self, application: Application):
        """Test that usage_panel_hook preserves existing panels in info_panel."""
        from byte import Payload
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        existing_panel = "existing panel"
        payload = Payload(EventType.POST_PROMPT_TOOLKIT, data={"info_panel": [existing_panel]})
        result = await service.usage_panel_hook(payload)

        info_panel = result.get("info_panel", [])
        assert len(info_panel) == 2
        assert info_panel[0] == existing_panel

    @pytest.mark.asyncio
    async def test_mixed_main_and_weak_usage(self, application: Application):
        """Test tracking usage across both main and weak models."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        # Main model usage
        main_usage = TokenUsageSchema(
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
        )
        await service.update_main_usage(main_usage)

        # Weak model usage
        weak_usage = TokenUsageSchema(
            input_tokens=200,
            output_tokens=100,
            total_tokens=300,
        )
        await service.update_weak_usage(weak_usage)

        assert service.usage.main.context == 1500
        assert service.usage.main.total.input == 1000
        assert service.usage.main.total.output == 500
        assert service.usage.weak.total.input == 200
        assert service.usage.weak.total.output == 100
        assert service.usage.last.type == "weak"

    @pytest.mark.asyncio
    async def test_last_message_tracks_most_recent_update(self, application: Application):
        """Test that last message usage tracks the most recent update."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        # First update (main)
        main_usage = TokenUsageSchema(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        )
        await service.update_main_usage(main_usage)

        assert service.usage.last.type == "main"
        assert service.usage.last.input == 100

        # Second update (weak)
        weak_usage = TokenUsageSchema(
            input_tokens=200,
            output_tokens=75,
            total_tokens=275,
        )
        await service.update_weak_usage(weak_usage)

        assert service.usage.last.type == "weak"
        assert service.usage.last.input == 200

    @pytest.mark.asyncio
    async def test_zero_token_usage(self, application: Application):
        """Test handling of zero token usage."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        token_usage = TokenUsageSchema(
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
        )

        await service.update_main_usage(token_usage)

        assert service.usage.main.context == 0
        assert service.usage.main.total.input == 0
        assert service.usage.main.total.output == 0

    @pytest.mark.asyncio
    async def test_large_token_counts(self, application: Application):
        """Test handling of very large token counts."""
        from byte.analytics import AgentAnalyticsService

        service = application.make(AgentAnalyticsService)

        token_usage = TokenUsageSchema(
            input_tokens=1000000,
            output_tokens=500000,
            total_tokens=1500000,
        )

        await service.update_main_usage(token_usage)

        assert service.usage.main.context == 1500000
        assert service.usage.main.total.input == 1000000
        assert service.usage.main.total.output == 500000
