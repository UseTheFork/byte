import fnmatch
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
from byte.support.yaml import Yaml


class ConstitutionService(Service):
    """Service for loading and managing the project constitution.

    The constitution is persisted as a directory of Markdown files with YAML
    frontmatter at ``app.config_path("constitution/")``.

    Layout::

        .byte/constitution/
            constitution.md          # frontmatter: version, ratified, last_amended
            principles/
                <id>.md            # frontmatter: name; body: description
            governance/
                <id>.md            # frontmatter: name; body: content
            sections/
                <id>/
                    section.md       # frontmatter: name, applies_to (list)
                    items/
                        <id>.md    # frontmatter: name; body: content

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
        self._constitution_path: Path = self.app.config_path("constitution")
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
        """Return the path to the constitution directory.

        Usage: `path = service.constitution_path`
        """
        return self._constitution_path

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def _save(self, constitution: Constitution) -> None:
        """Persist *constitution* to disk as a directory of Markdown files.

        Creates all required directories and files, removing stale slugs that
        no longer exist in the in-memory model.

        Usage: `self._save(constitution)`
        """
        root = self._constitution_path
        root.mkdir(parents=True, exist_ok=True)

        # --- constitution.md (meta) ---
        meta_file = root / "constitution.md"
        meta_file.write_text(
            Yaml.render_frontmatter(
                {
                    "version": constitution.meta.version,
                    "ratified": constitution.meta.ratified,
                    "last_amended": constitution.meta.last_amended,
                }
            ),
            encoding="utf-8",
        )

        # --- principles/ ---
        principles_dir = root / "principles"
        principles_dir.mkdir(exist_ok=True)
        active_principle_files: set[Path] = set()
        for slug, p in constitution.principles.items():
            f = principles_dir / f"{p.id}.md"
            f.write_text(
                Yaml.render_frontmatter({"id": p.id, "name": p.name, "order": p.order}, p.description), encoding="utf-8"
            )
            active_principle_files.add(f)
        # Remove stale files
        for existing in principles_dir.glob("*.md"):
            if existing not in active_principle_files:
                existing.unlink()

        # --- governance/ ---
        governance_dir = root / "governance"
        governance_dir.mkdir(exist_ok=True)
        active_governance_files: set[Path] = set()
        for slug, r in constitution.governance.items():
            f = governance_dir / f"{r.id}.md"
            f.write_text(
                Yaml.render_frontmatter({"id": r.id, "name": r.name, "order": r.order}, r.content), encoding="utf-8"
            )
            active_governance_files.add(f)
        for existing in governance_dir.glob("*.md"):
            if existing not in active_governance_files:
                existing.unlink()

        # --- sections/ ---
        sections_dir = root / "sections"
        sections_dir.mkdir(exist_ok=True)
        active_section_dirs: set[Path] = set()
        for slug, section in constitution.sections.items():
            section_dir = sections_dir / section.id
            section_dir.mkdir(exist_ok=True)
            active_section_dirs.add(section_dir)

            # section.md
            section_fm: dict = {"id": section.id, "name": section.name, "order": section.order}
            if section.applies_to:
                section_fm["applies_to"] = section.applies_to
            section_file = section_dir / "section.md"
            section_file.write_text(Yaml.render_frontmatter(section_fm), encoding="utf-8")

            # items/
            items_dir = section_dir / "items"
            items_dir.mkdir(exist_ok=True)
            active_item_files: set[Path] = set()
            for item_slug, item in section.items.items():
                f = items_dir / f"{item.id}.md"
                f.write_text(
                    Yaml.render_frontmatter(
                        {"id": item.id, "section_id": item.section_id, "name": item.name, "order": item.order},
                        item.content,
                    ),
                    encoding="utf-8",
                )
                active_item_files.add(f)
            for existing in items_dir.glob("*.md"):
                if existing not in active_item_files:
                    existing.unlink()

        # Remove stale section directories
        if sections_dir.exists():
            for existing_dir in [d for d in sections_dir.iterdir() if d.is_dir()]:
                if existing_dir not in active_section_dirs:
                    import shutil

                    shutil.rmtree(existing_dir)

        self.app["log"].debug(f"ConstitutionService: saved constitution to {root}")

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_constitution(self) -> Constitution:
        """Return the currently loaded Constitution.

        Usage: `c = service.get_constitution()`
        """
        assert self._constitution
        return self._constitution

    def get_constitution_for_path(self, paths: list[str | Path] | None = None) -> Constitution | None:
        """Return a filtered Constitution containing only sections relevant to *paths*.

        Sections without ``applies_to`` (global) are always included.
        Sections with ``applies_to`` are included only when at least one glob
        pattern matches any of the given paths.  Principles, governance rules,
        and metadata are always returned unchanged.

        When *paths* is ``None`` the constitution is returned as-is with all
        sections included.

        Args:
            paths: One or more file paths to match against section ``applies_to``
                   patterns, or ``None`` to return the full constitution.

        Returns:
            A new Constitution instance with filtered sections, or None if no
            constitution is loaded.

        Usage:
            `c = service.get_constitution_for_path(None)`
            `c = service.get_constitution_for_path(["src/byte/node/agents/foo.py", "src/byte/other.py"])`
        """
        if not self._constitution:
            return None

        if paths is None:
            return self._constitution

        str_paths = [str(p) for p in paths]
        filtered_sections: dict[str, ConstitutionSection] = {}

        for key, section in self._constitution.sections.items():
            if not section.applies_to:
                filtered_sections[key] = section
            elif any(fnmatch.fnmatch(str_path, pattern) for str_path in str_paths for pattern in section.applies_to):
                filtered_sections[key] = section

        return Constitution(
            principles=self._constitution.principles,
            governance=self._constitution.governance,
            meta=self._constitution.meta,
            sections=filtered_sections,
        )

    # ------------------------------------------------------------------
    # Principles
    # ------------------------------------------------------------------

    def add_principle(self, name: str, description: str, order: int = 0) -> ConstitutionPrinciple:
        """Add a new principle to the constitution and persist.

        Args:
            name:        Display name (e.g. "I. Library-First").
            description: Full text of the principle.
            order:       Display order (e.g. 1, 2, 3).

        Raises:
            ValueError: If no constitution is loaded or the slug already exists.

        Usage: `service.add_principle("I. Library-First", "Every feature starts as a library.")`
        """
        assert self._constitution
        slug = Str.normalize_id(name)
        if slug in self._constitution.principles:
            raise ValueError(f"Principle with slug '{slug}' already exists.")
        principle = ConstitutionPrinciple(id=slug, name=name, description=description, order=order)
        self._constitution.principles[slug] = principle
        self._save(self._constitution)
        return principle

    def delete_principle(self, principle_id: str) -> None:
        """Remove a principle by id and persist.

        Args:
            principle_id: ID of the principle to remove.

        Raises:
            ValueError: If no constitution is loaded or the principle is not found.

        Usage: `service.delete_principle("principle-1")`
        """
        assert self._constitution
        principle_slug = None
        for slug, p in self._constitution.principles.items():
            if p.id == principle_id:
                principle_slug = slug
                break
        if principle_slug is None:
            raise ValueError(f"Principle with id '{principle_id}' not found.")
        del self._constitution.principles[principle_slug]
        principle_file = self._constitution_path / "principles" / f"{principle_slug}.md"
        if principle_file.exists():
            principle_file.unlink()
        self._save(self._constitution)

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def add_section(self, name: str, applies_to: list[str] | None = None, order: int = 0) -> ConstitutionSection:
        """Add a new empty section to the constitution and persist.

        Args:
            name:       Display name of the section.
            applies_to: Optional glob patterns scoping the section to specific files.
            order:      Display order (e.g. 1, 2, 3).

        Raises:
            ValueError: If no constitution is loaded or the slug already exists.

        Usage: `service.add_section("Security Requirements", applies_to=["src/byte/node/**"])`
        """
        assert self._constitution
        slug = Str.normalize_id(name)
        if slug in self._constitution.sections:
            raise ValueError(f"Section with slug '{slug}' already exists.")
        section = ConstitutionSection(id=slug, name=name, applies_to=applies_to, order=order)
        self._constitution.sections[slug] = section
        self._save(self._constitution)
        return section

    def delete_section(self, section_id: str) -> None:
        """Remove a section by id and persist.

        Args:
            section_id: ID of the section to remove.

        Raises:
            ValueError: If no constitution is loaded or the section is not found.

        Usage: `service.delete_section("section-1")`
        """
        assert self._constitution
        section_slug = None
        for slug, section in self._constitution.sections.items():
            if section.id == section_id:
                section_slug = slug
                break
        if section_slug is None:
            raise ValueError(f"Section with id '{section_id}' not found.")
        del self._constitution.sections[section_slug]
        self._save(self._constitution)

    # ------------------------------------------------------------------
    # Section items
    # ------------------------------------------------------------------

    def add_section_item(self, section_id: str, item_name: str, content: str, order: int = 0) -> ConstitutionItem:
        """Add a named item to an existing section and persist.

        Args:
            section_id: ID of the parent section.
            item_name:  Display name of the new item.
            content:    Content of the item.
            order:      Display order (e.g. 1, 2, 3).

        Raises:
            ValueError: If no constitution is loaded, the section is not found,
                        or an item with the same slug already exists in that section.

        Usage: `service.add_section_item("section-1", "Secret Management", "All secrets in env vars.")`
        """
        assert self._constitution
        # Find the section by id
        section = None
        for slug, sec in self._constitution.sections.items():
            if sec.id == section_id:
                section = sec
                break
        if section is None:
            raise ValueError(f"Section with id '{section_id}' not found.")
        item_slug = Str.normalize_id(item_name)
        if item_slug in section.items:
            raise ValueError(f"Item '{item_name}' (slug: '{item_slug}') already exists in section '{section.name}'.")
        item = ConstitutionItem(id=item_slug, section_id=section.id, name=item_name, content=content, order=order)
        section.items[item_slug] = item
        self._save(self._constitution)
        return item

    def delete_section_item(self, section_id: str, item_id: str) -> None:
        """Remove an item from a section and persist.

        Args:
            section_id: ID of the parent section.
            item_id:    ID of the item to remove.

        Raises:
            ValueError: If no constitution is loaded, the section is not found,
                        or the item is not found within the section.

        Usage: `service.delete_section_item("section-1", "item-1")`
        """
        assert self._constitution
        # Find the section by id
        section = None
        for slug, sec in self._constitution.sections.items():
            if sec.id == section_id:
                section = sec
                break
        if section is None:
            raise ValueError(f"Section with id '{section_id}' not found.")
        # Find the item by id
        item_slug = None
        for slug, item in section.items.items():
            if item.id == item_id:
                item_slug = slug
                break
        if item_slug is None:
            raise ValueError(f"Item with id '{item_id}' not found in section '{section.name}'.")
        del section.items[item_slug]
        self._save(self._constitution)

    # ------------------------------------------------------------------
    # Governance rules
    # ------------------------------------------------------------------

    def add_governance_rule(self, name: str, content: str, order: int = 0) -> ConstitutionGovernanceRule:
        """Add a named governance rule and persist.

        Args:
            name:    Display name of the rule.
            content: Content of the rule.
            order:   Display order (e.g. 1, 2, 3).

        Raises:
            ValueError: If no constitution is loaded or a rule with the same slug already exists.

        Usage: `service.add_governance_rule("Supremacy", "Constitution supersedes all other practices.")`
        """
        assert self._constitution
        slug = Str.normalize_id(name)
        if slug in self._constitution.governance:
            raise ValueError(f"Governance rule with slug '{slug}' already exists.")
        rule = ConstitutionGovernanceRule(id=slug, name=name, content=content, order=order)
        self._constitution.governance[slug] = rule
        self._save(self._constitution)
        return rule

    def delete_governance_rule(self, rule_id: str) -> None:
        """Remove a governance rule by id and persist.

        Args:
            rule_id: ID of the governance rule to remove.

        Raises:
            ValueError: If no constitution is loaded or the rule is not found.

        Usage: `service.delete_governance_rule("governance-1")`
        """
        assert self._constitution
        rule_slug = None
        for slug, r in self._constitution.governance.items():
            if r.id == rule_id:
                rule_slug = slug
                break
        if rule_slug is None:
            raise ValueError(f"Governance rule with id '{rule_id}' not found.")
        del self._constitution.governance[rule_slug]
        self._save(self._constitution)

    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------

    def update_meta(
        self,
        ratification_date: str | None = None,
        last_amended_date: str | None = None,
        version: str | None = None,
    ) -> ConstitutionMeta:
        """Update constitution metadata fields and persist.

        Args:
            ratification_date: New RATIFICATION_DATE value (ISO 8601). Omit to keep current.
            last_amended_date: New LAST_AMENDED_DATE value (ISO 8601). Omit to keep current.
            version:           New CONSTITUTION_VERSION string. Omit to keep current.

        Raises:
            RuntimeError: If no constitution is loaded.

        Usage: `meta = service.update_meta(version="1.1.0", last_amended_date="2026-05-08")`
        """
        assert self._constitution
        meta = self._constitution.meta
        if ratification_date is not None:
            meta.ratified = ratification_date
        if last_amended_date is not None:
            meta.last_amended = last_amended_date
        if version is not None:
            meta.version = version
        self._save(self._constitution)
        return meta

    # ------------------------------------------------------------------
    # Directory loader
    # ------------------------------------------------------------------

    def _load_from_directory(self, root: Path) -> Constitution:
        """Parse the constitution from a directory of Markdown files.

        Args:
            root: The constitution root directory (e.g. ``.byte/constitution``).

        Returns:
            A fully populated Constitution instance.
        """
        # --- meta ---
        meta_file = root / "constitution.md"
        meta = ConstitutionMeta(version="0.1.0", ratified="", last_amended="")
        if meta_file.exists():
            fm, _ = Yaml.parse_frontmatter(meta_file.read_text(encoding="utf-8"))
            meta = ConstitutionMeta(
                version=str(fm.get("version", "0.1.0")),
                ratified=str(fm.get("ratified", "")),
                last_amended=str(fm.get("last_amended", "")),
            )

        # --- principles ---
        principles: dict[str, ConstitutionPrinciple] = {}
        principles_dir = root / "principles"
        if principles_dir.is_dir():
            for f in sorted(principles_dir.glob("*.md")):
                fm, body = Yaml.parse_frontmatter(f.read_text(encoding="utf-8"))
                name = fm.get("name")
                if not name:
                    self.app["log"].warning(f"ConstitutionService: missing 'name' in {f}, skipping")
                    continue
                principle_id = str(fm.get("id", ""))
                principles[principle_id] = ConstitutionPrinciple(
                    id=principle_id, name=str(name), description=body, order=int(fm.get("order", 1))
                )

        # --- governance ---
        governance: dict[str, ConstitutionGovernanceRule] = {}
        governance_dir = root / "governance"
        if governance_dir.is_dir():
            for f in sorted(governance_dir.glob("*.md")):
                fm, body = Yaml.parse_frontmatter(f.read_text(encoding="utf-8"))
                name = fm.get("name")
                if not name:
                    self.app["log"].warning(f"ConstitutionService: missing 'name' in {f}, skipping")
                    continue
                rule_id = str(fm.get("id", ""))
                governance[rule_id] = ConstitutionGovernanceRule(
                    id=rule_id, name=str(name), content=body, order=int(fm.get("order", 1))
                )

        # --- sections ---
        sections: dict[str, ConstitutionSection] = {}
        sections_dir = root / "sections"
        if sections_dir.is_dir():
            for section_dir in sorted(d for d in sections_dir.iterdir() if d.is_dir()):
                section_file = section_dir / "section.md"
                if not section_file.exists():
                    self.app["log"].warning(
                        f"ConstitutionService: section directory {section_dir} missing section.md, skipping"
                    )
                    continue
                fm, _ = Yaml.parse_frontmatter(section_file.read_text(encoding="utf-8"))
                name = fm.get("name")
                if not name:
                    self.app["log"].warning(f"ConstitutionService: missing 'name' in {section_file}, skipping")
                    continue
                applies_to = fm.get("applies_to") or None
                if applies_to is not None and not isinstance(applies_to, list):
                    applies_to = [str(applies_to)]

                items: dict[str, ConstitutionItem] = {}
                items_dir = section_dir / "items"
                if items_dir.is_dir():
                    for item_file in sorted(items_dir.glob("*.md")):
                        ifm, ibody = Yaml.parse_frontmatter(item_file.read_text(encoding="utf-8"))
                        iname = ifm.get("name")
                        if not iname:
                            self.app["log"].warning(f"ConstitutionService: missing 'name' in {item_file}, skipping")
                            continue
                        item_id = str(ifm.get("id", ""))
                        items[item_id] = ConstitutionItem(
                            id=item_id,
                            section_id=str(ifm.get("section_id", "")),
                            name=str(iname),
                            content=ibody,
                            order=int(ifm.get("order", 1)),
                        )

                section_id = str(fm.get("id", ""))
                sections[section_id] = ConstitutionSection(
                    id=section_id,
                    name=str(name),
                    items=items,
                    applies_to=applies_to,
                    order=int(fm.get("order", 1)),
                )

        return Constitution(
            principles=principles,
            governance=governance,
            meta=meta,
            sections=sections,
        )

    def save_and_set_current(self, constitution: Constitution) -> None:
        """Erase the constitution directory, save the provided constitution, and set it as current.

        Args:
            constitution: The Constitution instance to save and set as current.

        Usage: `service.save_and_set_current(constitution)`
        """
        import shutil

        root = self._constitution_path

        # Erase existing constitution directory
        if root.exists():
            shutil.rmtree(root)

        # Recreate directory and save the constitution
        root.mkdir(parents=True, exist_ok=True)
        self._save(constitution)

        # Set as current constitution
        self._constitution = constitution

        self.app["log"].debug(f"ConstitutionService: saved and set current constitution to {root}")

    def reload(self) -> None:
        """Re-read the constitution directory from disk.

        Silently creates a blank constitution if the directory does not exist yet;
        logs a warning if individual files cannot be parsed.

        Usage: `service.reload()`
        """
        root = self._constitution_path

        try:
            self._constitution = self._load_from_directory(root)
            self.app["log"].debug(
                f"ConstitutionService: loaded constitution v{self._constitution.meta.version} from {root}"
            )
        except Exception as exc:
            self.app["log"].warning(f"ConstitutionService: failed to load constitution from {root}: {exc}")
            self._constitution = None
