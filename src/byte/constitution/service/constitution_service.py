import fnmatch
import re
from pathlib import Path

import yaml

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

FRONTMATTER_PATTERN = re.compile(r"^---[\r\n]+(.*?)[\r\n]+---", re.DOTALL | re.MULTILINE)


class ConstitutionService(Service):
    """Service for loading and managing the project constitution.

    The constitution is persisted as a directory of Markdown files with YAML
    frontmatter at ``app.config_path("constitution/")``.

    Layout::

        .byte/constitution/
            constitution.md          # frontmatter: version, ratified, last_amended
            principles/
                <slug>.md            # frontmatter: name; body: description
            governance/
                <slug>.md            # frontmatter: name; body: content
            sections/
                <slug>/
                    section.md       # frontmatter: name, applies_to (list)
                    items/
                        <slug>.md    # frontmatter: name; body: content

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
            principles={Str.slugify(example.name): example},
            governance={Str.slugify(default_rule.name): default_rule},
            meta=ConstitutionMeta(version="0.1.0", ratified=today, last_amended=today),
        )

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _render_md(frontmatter: dict, body: str = "") -> str:
        """Render a Markdown file with YAML frontmatter.

        Args:
            frontmatter: Mapping to serialise as YAML between ``---`` fences.
            body:        Optional Markdown body appended after the closing fence.

        Returns:
            Complete file content string.
        """
        fm = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True).rstrip()
        parts = [f"---\n{fm}\n---"]
        if body:
            parts.append(body.strip())
        return "\n".join(parts) + "\n"

    @staticmethod
    def _parse_md(text: str) -> tuple[dict, str]:
        """Parse a Markdown file into (frontmatter dict, body string).

        Args:
            text: Raw file content.

        Returns:
            ``(frontmatter, body)`` where *frontmatter* is an empty dict when
            no YAML block is found and *body* is the remaining content after the
            closing ``---``.
        """
        match = FRONTMATTER_PATTERN.match(text)
        if not match:
            return {}, text.strip()
        fm = yaml.safe_load(match.group(1)) or {}
        body = text[match.end() :].strip()
        return fm, body

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
            self._render_md(
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
            f = principles_dir / f"{slug}.md"
            f.write_text(self._render_md({"name": p.name}, p.description), encoding="utf-8")
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
            f = governance_dir / f"{slug}.md"
            f.write_text(self._render_md({"name": r.name}, r.content), encoding="utf-8")
            active_governance_files.add(f)
        for existing in governance_dir.glob("*.md"):
            if existing not in active_governance_files:
                existing.unlink()

        # --- sections/ ---
        sections_dir = root / "sections"
        sections_dir.mkdir(exist_ok=True)
        active_section_dirs: set[Path] = set()
        for slug, section in constitution.sections.items():
            section_dir = sections_dir / slug
            section_dir.mkdir(exist_ok=True)
            active_section_dirs.add(section_dir)

            # section.md
            section_fm: dict = {"name": section.name}
            if section.applies_to:
                section_fm["applies_to"] = section.applies_to
            section_file = section_dir / "section.md"
            section_file.write_text(self._render_md(section_fm), encoding="utf-8")

            # items/
            items_dir = section_dir / "items"
            items_dir.mkdir(exist_ok=True)
            active_item_files: set[Path] = set()
            for item_slug, item in section.items.items():
                f = items_dir / f"{item_slug}.md"
                f.write_text(self._render_md({"name": item.name}, item.content), encoding="utf-8")
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

    def get_constitution_for_path(self, paths: list[str | Path] | None = None) -> Constitution:
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
        assert self._constitution

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

    def add_principle(self, name: str, description: str) -> ConstitutionPrinciple:
        """Add a new principle to the constitution and persist.

        Args:
            name:        Display name (e.g. "I. Library-First").
            description: Full text of the principle.

        Raises:
            ValueError: If no constitution is loaded or the slug already exists.

        Usage: `service.add_principle("I. Library-First", "Every feature starts as a library.")`
        """
        assert self._constitution
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
        assert self._constitution
        slug = Str.slugify(name)
        if slug not in self._constitution.principles:
            raise ValueError(f"Principle '{name}' (slug: '{slug}') not found.")
        del self._constitution.principles[slug]
        principle_file = self._constitution_path / "principles" / f"{slug}.md"
        if principle_file.exists():
            principle_file.unlink()
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
        assert self._constitution
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
        assert self._constitution
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
        assert self._constitution
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
        assert self._constitution
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
        assert self._constitution
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
        assert self._constitution
        slug = Str.slugify(name)
        if slug not in self._constitution.governance:
            raise ValueError(f"Governance rule '{name}' (slug: '{slug}') not found.")
        del self._constitution.governance[slug]
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
            fm, _ = self._parse_md(meta_file.read_text(encoding="utf-8"))
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
                fm, body = self._parse_md(f.read_text(encoding="utf-8"))
                name = fm.get("name")
                if not name:
                    self.app["log"].warning(f"ConstitutionService: missing 'name' in {f}, skipping")
                    continue
                slug = f.stem
                principles[slug] = ConstitutionPrinciple(name=str(name), description=body)

        # --- governance ---
        governance: dict[str, ConstitutionGovernanceRule] = {}
        governance_dir = root / "governance"
        if governance_dir.is_dir():
            for f in sorted(governance_dir.glob("*.md")):
                fm, body = self._parse_md(f.read_text(encoding="utf-8"))
                name = fm.get("name")
                if not name:
                    self.app["log"].warning(f"ConstitutionService: missing 'name' in {f}, skipping")
                    continue
                slug = f.stem
                governance[slug] = ConstitutionGovernanceRule(name=str(name), content=body)

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
                fm, _ = self._parse_md(section_file.read_text(encoding="utf-8"))
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
                        ifm, ibody = self._parse_md(item_file.read_text(encoding="utf-8"))
                        iname = ifm.get("name")
                        if not iname:
                            self.app["log"].warning(f"ConstitutionService: missing 'name' in {item_file}, skipping")
                            continue
                        item_slug = item_file.stem
                        items[item_slug] = ConstitutionItem(name=str(iname), content=ibody)

                slug = section_dir.name
                sections[slug] = ConstitutionSection(name=str(name), items=items, applies_to=applies_to)

        return Constitution(
            principles=principles,
            governance=governance,
            meta=meta,
            sections=sections,
        )

    def reload(self) -> None:
        """Re-read the constitution directory from disk.

        Silently creates a blank constitution if the directory does not exist yet;
        logs a warning if individual files cannot be parsed.

        Usage: `service.reload()`
        """
        root = self._constitution_path

        if not root.exists():
            self.app["log"].debug(
                f"ConstitutionService: no constitution directory found at {root}, creating blank constitution"
            )
            self._constitution = self._create_blank()
            self._save(self._constitution)
            return

        try:
            self._constitution = self._load_from_directory(root)
            self.app["log"].debug(
                f"ConstitutionService: loaded constitution v{self._constitution.meta.version} from {root}"
            )
        except Exception as exc:
            self.app["log"].warning(f"ConstitutionService: failed to load constitution from {root}: {exc}")
            self._constitution = None
