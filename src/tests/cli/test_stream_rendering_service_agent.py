from __future__ import annotations

import io
from typing import TYPE_CHECKING

import pytest
from pytest_mock import MockerFixture
from rich.console import Console as RichConsole

from byte.agent import AskAgent
from byte.cli import CLIServiceProvider
from tests.base_test import BaseTest

if TYPE_CHECKING:
    from byte import Application


class TestStreamRenderingService(BaseTest):
    """"""

    @pytest.fixture
    def providers(self):
        """Provide service providers for coder agent tests."""
        from byte.agent import AgentServiceProvider
        from byte.files import FileServiceProvider

        return [AgentServiceProvider, FileServiceProvider, CLIServiceProvider]

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_silent_mode_produces_no_console_output(
        self,
        application: Application,
        mocker: MockerFixture,
    ):
        """Test that agent execution in silent mode produces no console output."""

        string_io = io.StringIO()
        console = RichConsole(file=string_io)
        console_service = application["console"]
        mocker.patch.object(console_service, "_console", console)

        # Create the agent
        agent = application.make(AskAgent)

        # Request to create a new file
        request = "Create a new file called hello.py with a simple hello world function"

        await agent.execute(request, display_mode="silent")

        captured_output = string_io.getvalue()

        application["log"].info(captured_output)

        assert captured_output == ""

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_thinking_mode_produces_spinner_console_output(
        self,
        application: Application,
        mocker: MockerFixture,
    ):
        """Test that agent execution in thinking mode produces no console output."""

        string_io = io.StringIO()
        console = RichConsole(file=string_io)
        console_service = application["console"]
        mocker.patch.object(console_service, "_console", console)

        # Create the agent
        agent = application.make(AskAgent)

        # Request to create a new file
        request = "Create a new file called hello.py with a simple hello world function"

        await agent.execute(request, display_mode="thinking")

        captured_output = string_io.getvalue()

        assert "Thinking..." in captured_output
        assert "Ask Agent" not in captured_output

    @pytest.mark.asyncio
    @pytest.mark.vcr
    async def test_verbose_mode_produces_all_console_output(
        self,
        application: Application,
        mocker: MockerFixture,
    ):
        """Test that agent execution in verbose mode produces full console output including spinner and agent name."""

        string_io = io.StringIO()
        console = RichConsole(file=string_io)
        console_service = application["console"]
        mocker.patch.object(console_service, "_console", console)

        # Create the agent
        agent = application.make(AskAgent)

        # Request to create a new file
        request = "Create a new file called hello.py with a simple hello world function"

        await agent.execute(request, display_mode="verbose")

        captured_output = string_io.getvalue()

        # application["log"].info(application["env"])

        assert "Thinking..." in captured_output
        assert "Ask Agent" in captured_output
