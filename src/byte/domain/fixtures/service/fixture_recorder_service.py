"""Service for recording node and graph responses as JSON fixtures for testing.

Hooks into the event system to capture responses at key execution points and
serializes them to JSON files organized by agent type, node name, and scenario.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from langchain.load.dump import dumps

from byte.core.event_bus import Payload
from byte.core.service.base_service import Service


class FixtureRecorderService(Service):
    """Domain service for recording agent responses as reusable JSON fixtures.

    Captures state snapshots from nodes and graphs, serializing them to organized
    JSON files that can be loaded in tests. Supports scenario-based recording and
    automatic fixture organization by agent/node type.

    Usage: Enable via config or environment variable, then responses are automatically
           captured and saved to tests/fixtures/ during execution.
    """

    _recording_enabled: bool
    _fixture_scenario: Optional[str]
    _fixtures_dir: Path
    _recorded_count: int

    async def boot(self):
        """Initialize the fixture recorder with configuration from environment."""
        # Check if recording is enabled via config or environment
        self._recording_enabled = False
        self._fixture_scenario = None
        self._recorded_count = 0

        if self._config:
            # Read from environment or config
            self._recording_enabled = (
                os.getenv("BYTE_RECORD_FIXTURES", "false").lower() == "true"
            )
            self._fixture_scenario = os.getenv("BYTE_FIXTURE_SCENARIO")

            # Set fixtures directory relative to project root
            if self._config.project_root:
                self._fixtures_dir = (
                    self._config.project_root / "src" / "tests" / "fixtures"
                )
            else:
                self._fixtures_dir = Path("tests/fixtures")

    async def record_assistant_node_response(self, payload: Payload) -> Payload:
        """Capture and record assistant node responses to fixture files.

        Hooks into POST_ASSISTANT_NODE event to capture the complete state
        after the assistant node processes. Saves the entire state for replay.

        Usage: Automatically called when POST_ASSISTANT_NODE event fires
        """
        if not self._recording_enabled:
            return payload

        state = payload.get("state")
        if not state:
            return payload

        # Prepare fixture data with full state
        fixture_data = {
            "metadata": {
                "recorded_at": datetime.now().isoformat(),
                "scenario": self._fixture_scenario,
                "node": "assistant_node",
                "agent": state.get("agent", "unknown"),
                "thread_id": payload.get("thread_id"),
            },
            "state": dumps(state),
        }

        # Save the fixture
        await self._save_fixture(fixture_data, state.get("agent"))

        return payload

    async def _save_fixture(
        self, fixture_data: Dict[str, Any], agent_name: Optional[str]
    ) -> None:
        """Save fixture data to an organized JSON file.

        Creates directory structure: fixtures/{agent}/{node_name}/
        Generates filename from scenario and timestamp if no scenario provided.

        Args:
            node_name: Name of the node that generated the fixture
            fixture_data: Dictionary containing the fixture data to save
            agent_name: Name of the agent (e.g., 'CoderAgent')
        """
        # Determine agent directory name
        if agent_name:
            # Convert 'CoderAgent' to 'coder'
            agent = agent_name.replace("Agent", "").lower()
        else:
            agent = "unknown"

        # Create directory structure
        fixture_dir = self._fixtures_dir / "recorded"
        fixture_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        if self._fixture_scenario:
            filename = f"{self._fixture_scenario}.json"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{agent}_{timestamp}_{self._recorded_count}.json"
            self._recorded_count += 1

        fixture_path = fixture_dir / filename

        # Write fixture data as formatted JSON
        with open(fixture_path, "w", encoding="utf-8") as f:
            json.dump(fixture_data, f, indent=2, ensure_ascii=False)

    def is_recording_enabled(self) -> bool:
        """Check if fixture recording is currently enabled.

        Returns:
            bool: True if recording is enabled, False otherwise

        Usage: `if recorder.is_recording_enabled(): ...`
        """
        return self._recording_enabled

    def get_fixture_scenario(self) -> Optional[str]:
        """Get the current fixture recording scenario name.

        Returns:
            Optional[str]: Scenario name if set, None otherwise

        Usage: `scenario = recorder.get_fixture_scenario()`
        """
        return self._fixture_scenario
