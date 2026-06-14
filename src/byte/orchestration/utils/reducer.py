from byte.orchestration import ConstraintSchema, MetadataSchema


class Reducer:
    """Provide state reducers for LangGraph annotations."""

    @staticmethod
    def replace_list(left: list | None, right: list) -> list:
        """Replace the entire list with new values."""
        return right

    @staticmethod
    def replace_str(left: str | None, right: str | None) -> str | None:
        """Replace the string with a new value."""
        return right

    @staticmethod
    def add_constraints(left: list[ConstraintSchema] | None, right: list[ConstraintSchema]) -> list[ConstraintSchema]:
        """Accumulate user-defined constraints for the current invocation."""
        if left is None:
            return right
        return left + right

    @staticmethod
    def update_metadata(left: MetadataSchema | None, right: MetadataSchema) -> MetadataSchema:
        """Replace the old metadata with the new metadata."""
        return right

    @staticmethod
    def add_touched_files(left: list[str] | None, right: list[str]) -> list[str]:
        """Accumulate touched files and remove duplicates."""
        if left is None:
            return right

        return list(set(left + right))
