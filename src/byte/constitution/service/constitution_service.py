import fnmatch
import json
from pathlib import Path

from byte import Service
from byte.constitution.models import (
    Constitution,
    ConstitutionGovernanceRule,
    ConstitutionItem,
    ConstitutionMeta,
    ConstitutionPrinciple,
    ConstitutionSection,
)
from byte.support.string import Str


class ConstitutionService(Service):
    """Service for loading and managing the project constitution.

    The constitution is persisted as a JSON file at
    ``app.config_path("constitution.json")`` and is loaded on boot.

    Usage:
        service = app.make(ConstitutionService)
        constitution = service.constitution   # access the loaded Constitution
        service.reload()                      # re-read from disk
    """

    def boot(self) -> None:
        """Initialise the service and load the constitution from disk.

        Usage: called automatically when the service provider boots.
        """
        self._constitution: Constitution | None = None
        self._constitution_path: Path = self.app.config_path("constitution.json")
        self.reload()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def constitution(self) -> Constitution | None:
        """Return the currently loaded Constitution, or None if not found.

        Usage: `c = service.constitution`
        """
        return self._constitution

    @property
    def constitution_path(self) -> Path:
        """Return the path to the constitution JSON file.

        Usage: `path = service.constitution_path`
        """
        return self._constitution_path

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _create_blank(self) -> Constitution:
        """Create a blank Constitution with sensible defaults.

        Usage: `c = self._create_blank()`
        """

        today = __import__("datetime").date.today().isoformat()
        example = ConstitutionPrinciple(
            name="I. Example Principle",
            description="Describe your first core principle here.",
        )
        default_rule = ConstitutionGovernanceRule(
            name="Supremacy",
            content="Constitution supersedes all other practices. Amendments require documentation and approval.",
        )
        return Constitution(
            project_name="Untitled Constitution",
            principles={Str.slugify(example.name): example},
            governance={Str.slugify(default_rule.name): default_rule},
            meta=ConstitutionMeta(version="0.1.0", ratified=today, last_amended=today),
        )

    def _save(self, constitution: Constitution) -> None:
        """Persist *constitution* to disk as JSON.

        Creates parent directories if they do not exist.

        Usage: `self._save(constitution)`
        """
        path = self._constitution_path
        path.write_text(json.dumps(constitution.to_dict(), indent=2), encoding="utf-8")
        self.app["log"].debug(f"ConstitutionService: saved constitution to {path}")

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_constitution(self) -> Constitution | None:
        """Return the currently loaded Constitution, or None if not loaded.

        Usage: `c = service.get_constitution()`
        """
        return self._constitution

    def get_constitution_for_path(self, path: str | Path) -> Constitution | None:
        """Return a filtered Constitution containing only sections relevant to *path*.

        Sections without ``applies_to`` (global) are always included.
        Sections with ``applies_to`` are included only when at least one glob
        pattern matches *path*.  Principles, governance rules, and metadata are
        always returned unchanged.

        Args:
            path: File path to match against section ``applies_to`` patterns.

        Returns:
            A new Constitution instance with filtered sections, or None if no
            constitution is loaded.

        Usage: `c = service.get_constitution_for_path("src/byte/node/agents/foo.py")`
        """
        if self._constitution is None:
            return None

        str_path = str(path)
        filtered_sections: dict[str, ConstitutionSection] = {}

        for key, section in self._constitution.sections.items():
            if not section.applies_to:
                # Global section — always include
                filtered_sections[key] = section
            elif any(fnmatch.fnmatch(str_path, pattern) for pattern in section.applies_to):
                filtered_sections[key] = section

        return Constitution(
            project_name=self._constitution.project_name,
            principles=self._constitution.principles,
            governance=self._constitution.governance,
            meta=self._constitution.meta,
            sections=filtered_sections,
        )

    # ------------------------------------------------------------------
    # Internal guards
    # ------------------------------------------------------------------

    def _require_constitution(self) -> None:
        """Raise RuntimeError if no constitution is currently loaded.

        Usage: `self._require_constitution()`
        """
        if self._constitution is None:
            raise RuntimeError("No constitution is loaded. Call reload() first.")

    # ------------------------------------------------------------------
    # Principles
    # ------------------------------------------------------------------

    def add_principle(self, name: str, description: str) -> ConstitutionPrinciple:
        """Add a new principle to the constitution and persist.

        Args:
            name:        Display name (e.g. "I. Library-First").
            description: Full text of the principle.

        Raises:
            ValueError: If no constitution is loaded or the slug already exists.

        Usage: `service.add_principle("I. Library-First", "Every feature starts as a library.")`
        """
        self._require_constitution()
        slug = Str.slugify(name)
        if slug in self._constitution.principles:
            raise ValueError(f"Principle with slug '{slug}' already exists.")
        principle = ConstitutionPrinciple(name=name, description=description)
        self._constitution.principles[slug] = principle
        self._save(self._constitution)
        return principle

    def delete_principle(self, name: str) -> None:
        """Remove a principle by name (or slug) and persist.

        Args:
            name: Display name or slug of the principle to remove.

        Raises:
            ValueError: If no constitution is loaded or the principle is not found.

        Usage: `service.delete_principle("I. Library-First")`
        """
        self._require_constitution()
        slug = Str.slugify(name)
        if slug not in self._constitution.principles:
            raise ValueError(f"Principle '{name}' (slug: '{slug}') not found.")
        del self._constitution.principles[slug]
        self._save(self._constitution)

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def add_section(self, name: str, applies_to: list[str] | None = None) -> ConstitutionSection:
        """Add a new empty section to the constitution and persist.

        Args:
            name:       Display name of the section.
            applies_to: Optional glob patterns scoping the section to specific files.

        Raises:
            ValueError: If no constitution is loaded or the slug already exists.

        Usage: `service.add_section("Security Requirements", applies_to=["src/byte/node/**"])`
        """
        self._require_constitution()
        slug = Str.slugify(name)
        if slug in self._constitution.sections:
            raise ValueError(f"Section with slug '{slug}' already exists.")
        section = ConstitutionSection(name=name, applies_to=applies_to)
        self._constitution.sections[slug] = section
        self._save(self._constitution)
        return section

    def delete_section(self, name: str) -> None:
        """Remove a section by name (or slug) and persist.

        Args:
            name: Display name or slug of the section to remove.

        Raises:
            ValueError: If no constitution is loaded or the section is not found.

        Usage: `service.delete_section("Security Requirements")`
        """
        self._require_constitution()
        slug = Str.slugify(name)
        if slug not in self._constitution.sections:
            raise ValueError(f"Section '{name}' (slug: '{slug}') not found.")
        del self._constitution.sections[slug]
        self._save(self._constitution)

    # ------------------------------------------------------------------
    # Section items
    # ------------------------------------------------------------------

    def add_section_item(self, section_name: str, item_name: str, content: str) -> ConstitutionItem:
        """Add a named item to an existing section and persist.

        Args:
            section_name: Display name or slug of the parent section.
            item_name:    Display name of the new item.
            content:      Content of the item.

        Raises:
            ValueError: If no constitution is loaded, the section is not found,
                        or an item with the same slug already exists in that section.

        Usage: `service.add_section_item("Security Requirements", "Secret Management", "All secrets in env vars.")`
        """
        self._require_constitution()
        section_slug = Str.slugify(section_name)
        if section_slug not in self._constitution.sections:
            raise ValueError(f"Section '{section_name}' (slug: '{section_slug}') not found.")
        section = self._constitution.sections[section_slug]
        item_slug = Str.slugify(item_name)
        if item_slug in section.items:
            raise ValueError(f"Item '{item_name}' (slug: '{item_slug}') already exists in section '{section_name}'.")
        item = ConstitutionItem(name=item_name, content=content)
        section.items[item_slug] = item
        self._save(self._constitution)
        return item

    def delete_section_item(self, section_name: str, item_name: str) -> None:
        """Remove a named item from a section and persist.

        Args:
            section_name: Display name or slug of the parent section.
            item_name:    Display name or slug of the item to remove.

        Raises:
            ValueError: If no constitution is loaded, the section is not found,
                        or the item is not found within the section.

        Usage: `service.delete_section_item("Security Requirements", "Secret Management")`
        """
        self._require_constitution()
        section_slug = Str.slugify(section_name)
        if section_slug not in self._constitution.sections:
            raise ValueError(f"Section '{section_name}' (slug: '{section_slug}') not found.")
        section = self._constitution.sections[section_slug]
        item_slug = Str.slugify(item_name)
        if item_slug not in section.items:
            raise ValueError(f"Item '{item_name}' (slug: '{item_slug}') not found in section '{section_name}'.")
        del section.items[item_slug]
        self._save(self._constitution)

    # ------------------------------------------------------------------
    # Governance rules
    # ------------------------------------------------------------------

    def add_governance_rule(self, name: str, content: str) -> ConstitutionGovernanceRule:
        """Add a named governance rule and persist.

        Args:
            name:    Display name of the rule.
            content: Content of the rule.

        Raises:
            ValueError: If no constitution is loaded or a rule with the same slug already exists.

        Usage: `service.add_governance_rule("Supremacy", "Constitution supersedes all other practices.")`
        """
        self._require_constitution()
        slug = Str.slugify(name)
        if slug in self._constitution.governance:
            raise ValueError(f"Governance rule with slug '{slug}' already exists.")
        rule = ConstitutionGovernanceRule(name=name, content=content)
        self._constitution.governance[slug] = rule
        self._save(self._constitution)
        return rule

    def delete_governance_rule(self, name: str) -> None:
        """Remove a governance rule by name (or slug) and persist.

        Args:
            name: Display name or slug of the rule to remove.

        Raises:
            ValueError: If no constitution is loaded or the rule is not found.

        Usage: `service.delete_governance_rule("Supremacy")`
        """
        self._require_constitution()
        slug = Str.slugify(name)
        if slug not in self._constitution.governance:
            raise ValueError(f"Governance rule '{name}' (slug: '{slug}') not found.")
        del self._constitution.governance[slug]
        self._save(self._constitution)

    def reload(self) -> None:
        """Re-read the constitution JSON file from disk.

        Silently sets ``self._constitution`` to None if the file does not
        exist yet; logs a warning if the file exists but cannot be parsed.

        Usage: `service.reload()`
        """
        path = self._constitution_path

        if not path.exists():
            self.app["log"].debug(
                f"ConstitutionService: no constitution file found at {path}, creating blank constitution"
            )
            self._constitution = self._create_blank()
            self._save(self._constitution)
            return

        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            self._constitution = Constitution.from_dict(data)
            self.app["log"].debug(
                f"ConstitutionService: loaded constitution "
                f"'{self._constitution.project_name}' "
                f"v{self._constitution.meta.version} from {path}"
            )
        except (OSError, json.JSONDecodeError) as exc:
            self.app["log"].warning(f"ConstitutionService: failed to load constitution from {path}: {exc}")
            self._constitution = None
