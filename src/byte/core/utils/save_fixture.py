from datetime import datetime

import dill

from byte.core.config.config import PROJECT_ROOT
from byte.core.event_bus import Payload


class FixtureRecorder:
    @staticmethod
    def pickle_fixture(payload: Payload) -> None:
        """Capture and record assistant node responses to fixture files."""

        state = payload.get("state")
        if not state:
            return

        fixture_dir = PROJECT_ROOT / "src" / "tests" / "fixtures" / "recorded"
        fixture_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.pkl"

        fixture_path = fixture_dir / filename

        with open(fixture_path, "wb") as fp:
            dill.dump(state, fp)
