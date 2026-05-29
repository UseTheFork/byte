from byte.orchestration.state import BaseState, HarnessFiles, HarnessState


class HarnessStateUtils:
    """Harness state helper utilities."""

    @staticmethod
    def get_harness(state: BaseState) -> HarnessState:
        """Get the harness configuration from state."""
        return state.get("harness", {})

    @staticmethod
    def get_files(state: BaseState) -> HarnessFiles:
        """Get the files configuration from harness."""
        harness = HarnessStateUtils.get_harness(state)
        return harness.get("files", {"edit": None, "create": None, "test": None, "reference": None})

    @staticmethod
    def get_editable_files(state: BaseState) -> list[str]:
        """Get the list of files that can be edited."""
        return HarnessStateUtils.get_files(state).get("edit") or []

    @staticmethod
    def get_reference_files(state: BaseState) -> list[str]:
        """Get the list of reference files."""
        return HarnessStateUtils.get_files(state).get("reference") or []

    @staticmethod
    def get_create_files(state: BaseState) -> list[str]:
        """Get the list of files to create."""
        return HarnessStateUtils.get_files(state).get("create") or []

    @staticmethod
    def get_test_files(state: BaseState) -> list[str]:
        """Get the list of test files."""
        return HarnessStateUtils.get_files(state).get("test") or []

    @staticmethod
    def get_all_files(state: BaseState) -> list[str]:
        """Get all files from all categories, deduplicated and ordered."""
        files = HarnessStateUtils.get_files(state)
        all_files = (
            (files.get("edit") or [])
            + (files.get("create") or [])
            + (files.get("test") or [])
            + (files.get("reference") or [])
        )
        return list(dict.fromkeys(all_files))

    @staticmethod
    def set_files(state: BaseState, **kwargs) -> HarnessState:
        """Update the files configuration in harness with valid keys."""
        harness = HarnessStateUtils.get_harness(state)
        files = HarnessStateUtils.get_files(state)
        valid_keys = {"edit", "create", "test", "reference"}
        for key, value in kwargs.items():
            if key in valid_keys:
                files[key] = value  # ty:ignore[invalid-key]
        harness["files"] = files
        return harness

    @staticmethod
    def get_skills(state: BaseState) -> list[str]:
        """Get the list of available skills."""
        harness = HarnessStateUtils.get_harness(state)
        return harness.get("skills", [])

    @staticmethod
    def get_instruction(state: BaseState) -> str | None:
        """Get the instruction from harness."""
        harness = HarnessStateUtils.get_harness(state)
        return harness.get("instruction")

    @staticmethod
    def has_instruction(state: BaseState) -> bool:
        """Check if an instruction is present."""
        return bool(HarnessStateUtils.get_instruction(state))
