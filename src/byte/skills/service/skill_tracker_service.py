from byte import Service
from byte.skills.schemas import Skill


class SkillTrackerService(Service):
    """Service for tracking which skills have been loaded during a session.

    Maintains a dict of active skills keyed by name and tracks which ones have
    been loaded (read) during the current session. Only active skills can be
    marked as loaded, preventing misattribution when skills are overridden.
    Usage: `skill_tracker_service.mark_loaded("code-reviewer")`
    """

    def boot(self) -> None:
        """Initialize the tracker with empty loaded set and active skills dict.

        Usage: `service = SkillTrackerService(container)`
        """
        self._loaded: set[str] = set()
        self._active_names: dict[str, Skill] = {}

    def set_active_skills(self, skills: dict[str, Skill]) -> None:
        """Set the collection of active skills for this session.

        Only skills in the active dict can be marked as loaded. This prevents
        misattribution when a builtin skill is overridden by a user skill.

        Args:
            skills: Dict of active skills keyed by name (post-dedup, post-filter)

        Usage: `service.set_active_skills(skill_loader.skills)`
        """
        self._active_names = skills

    def mark_loaded(self, name: str) -> bool:
        """Mark a skill as having been loaded during this session.

        Only marks as loaded if the skill is in the active set. Silently
        ignores names that are not in the active skill set.

        Args:
            name: The skill name to mark as loaded

        Returns:
            True if the skill was marked as loaded, False otherwise

        Usage: `service.mark_loaded("code-reviewer")`
        """
        if name in self._active_names:
            self._loaded.add(name)
            return True
        return False

    def is_loaded(self, name: str) -> bool:
        """Return whether a skill has been loaded during this session.

        Args:
            name: The skill name to check

        Returns:
            True if the skill has been loaded, False otherwise

        Usage: `if service.is_loaded("code-reviewer"): ...`
        """
        return name in self._loaded

    def loaded_names(self) -> list[str]:
        """Return a sorted list of all skill names loaded during this session.

        Returns:
            Alphabetically sorted list of loaded skill names, or empty list
            if no skills have been loaded

        Usage: `names = service.loaded_names()`
        """
        return sorted(self._loaded)

    def loaded_count(self) -> int:
        """Return the number of unique skills loaded during this session.

        Returns:
            Count of loaded skills

        Usage: `count = service.loaded_count()`
        """
        return len(self._loaded)

    def reset(self) -> None:
        """Clear all loaded tracking state, keeping active names intact.

        Useful for resetting between sessions without needing to re-register
        active skill names.

        Usage: `service.reset()`
        """
        self._loaded = set()

    def get_unloaded_names(self) -> list[str]:
        """Return a sorted list of active skills that have NOT been loaded.

        Returns:
            Alphabetically sorted list of active skill names not yet loaded

        Usage: `unloaded = service.get_unloaded_names()`
        """
        return sorted(self._active_names.keys() - self._loaded)
