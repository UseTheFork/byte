from dataclasses import dataclass, field

from byte.support import Section, SectionType
from byte.support.string import Str
from byte.support.utils import list_to_multiline_text


@dataclass
class ConstitutionPrinciple:
    """A single named principle within the Core Principles section."""

    id: str
    name: str
    description: str
    order: int = 0


@dataclass
class ConstitutionItem:
    """A single named item within a ConstitutionSection.

    Using discrete items instead of a monolithic content string allows tools
    to perform surgical edits — only the targeted item's content needs to be
    replaced rather than the entire section blob.
    """

    id: str
    section_id: str
    name: str
    content: str
    order: int = 0


@dataclass
class ConstitutionGovernanceRule:
    """A single named governance rule within the Governance section.

    Keyed by slug in the parent dict for O(1) lookup and surgical edits.
    """

    id: str
    name: str
    content: str
    order: int = 0


@dataclass
class ConstitutionSection:
    """An arbitrary additional section (beyond Core Principles and Governance).

    Attributes:
        name:       Section heading.
        items:      Named items keyed by item name for O(1) lookup and surgical edits.
        applies_to: Optional list of glob patterns (e.g. ["src/byte/node/**"]).
                    When None or empty, the section applies to all files.
    """

    id: str
    name: str
    items: dict[str, ConstitutionItem] = field(default_factory=dict)
    applies_to: list[str] | None = None  # None = applies to all
    order: int = 0


@dataclass
class ConstitutionMeta:
    """Version / ratification metadata always present on a constitution."""

    version: str
    ratified: str
    last_amended: str


@dataclass
class Constitution:
    """In-memory representation of a project constitution.

    Required fields (always present):
        project_name:  e.g. "Spec Constitution"
        principles:    Core Principles keyed by slug for O(1) lookup.
        governance:    Named governance rules keyed by slug for O(1) lookup.
        meta:          version / ratification info

    Optional fields:
        sections:  additional named sections keyed by section name (e.g. "Security Requirements")
    """

    principles: dict[str, ConstitutionPrinciple]
    governance: dict[str, ConstitutionGovernanceRule]
    meta: ConstitutionMeta
    sections: dict[str, ConstitutionSection] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "principles": [
                {"id": p.id, "name": p.name, "description": p.description, "order": p.order}
                for p in self.principles.values()
            ],
            "governance": [
                {"id": r.id, "name": r.name, "content": r.content, "order": r.order} for r in self.governance.values()
            ],
            "meta": {
                "version": self.meta.version,
                "ratified": self.meta.ratified,
                "last_amended": self.meta.last_amended,
            },
            "sections": [
                {
                    "id": s.id,
                    "name": s.name,
                    "items": [
                        {"id": i.id, "section_id": i.section_id, "name": i.name, "content": i.content, "order": i.order}
                        for i in s.items.values()
                    ],
                    "order": s.order,
                    **({} if s.applies_to is None else {"applies_to": s.applies_to}),
                }
                for s in self.sections.values()
            ],
        }

    def to_markdown(self) -> str:
        """Render the constitution as a Markdown document.

        Produces output matching the canonical constitution template:
        project title → Core Principles → optional extra sections →
        Governance → version footer.

        Usage: `md = constitution.to_markdown()`
        """
        lines: list[str] = []

        # Title
        lines.append(Section.start(SectionType.CONSTITUTION))
        lines.append("")

        # Core Principles
        lines.append(Section.sub_heading("Core Principles", 2, True))
        lines.append("")
        for principle in sorted(self.principles.values(), key=lambda p: p.order):
            lines.append(Section.sub_heading(f"{principle.order}. {principle.name}", 3, True))
            lines.append(f"**ID**: `{principle.id}`")
            lines.append("")
            lines.append(principle.description)
            lines.append("")

        # Additional sections (each may be scoped to specific file patterns)
        for section in sorted(self.sections.values(), key=lambda s: s.order):
            lines.append(Section.sub_heading(section.name, 2, True))
            lines.append(f"**ID**: `{section.id}`")
            lines.append("")
            if section.applies_to:
                scopes = ", ".join(f"`{p}`" for p in section.applies_to)
                lines.append(f"*Applies to: {scopes}*")
                lines.append("")
            for item in sorted(section.items.values(), key=lambda i: i.order):
                lines.append(Section.sub_heading(item.name, 3, True))
                lines.append(f"**ID**: `{item.id}`")
                lines.append("")
                lines.append(item.content)
                lines.append("")

        # Governance
        lines.append(Section.sub_heading("Governance", 2, True))
        lines.append("")
        for rule in sorted(self.governance.values(), key=lambda r: r.order):
            lines.append(Section.sub_heading(rule.name, 3, True))
            lines.append(f"**ID**: `{rule.id}`")
            lines.append("")
            lines.append(rule.content)
            lines.append("")

        # Version footer
        lines.append(
            f"**Version**: {self.meta.version} | "
            f"**Ratified**: {self.meta.ratified} | "
            f"**Last Amended**: {self.meta.last_amended}"
        )
        lines.extend(
            [
                "",
                Section.end(),
            ]
        )
        return list_to_multiline_text(lines)

    @classmethod
    def from_dict(cls, data: dict) -> Constitution:
        principles: dict[str, ConstitutionPrinciple] = {}
        for p in data.get("principles", []):
            principle = ConstitutionPrinciple(
                id=p.get("id", ""), name=p["name"], description=p["description"], order=p.get("order", 0)
            )
            principles[Str.normalize_id(principle.name)] = principle

        sections: dict[str, ConstitutionSection] = {}
        for s in data.get("sections", []):
            items: dict[str, ConstitutionItem] = {}
            for i in s.get("items", []):
                item = ConstitutionItem(
                    id=i.get("id", ""),
                    section_id=i.get("section_id", ""),
                    name=i["name"],
                    content=i["content"],
                    order=i.get("order", 0),
                )
                items[Str.normalize_id(item.name)] = item

            section = ConstitutionSection(
                id=s.get("id", ""),
                name=s["name"],
                items=items,
                applies_to=s.get("applies_to"),
                order=s.get("order", 0),
            )
            sections[Str.normalize_id(section.name)] = section

        governance: dict[str, ConstitutionGovernanceRule] = {}
        for r in data.get("governance", []):
            rule = ConstitutionGovernanceRule(
                id=r.get("id", ""), name=r["name"], content=r["content"], order=r.get("order", 0)
            )
            governance[Str.normalize_id(rule.name)] = rule

        raw_meta = data.get("meta", {})
        meta = ConstitutionMeta(
            version=raw_meta.get("version", "0.0.1"),
            ratified=raw_meta.get("ratified", ""),
            last_amended=raw_meta.get("last_amended", ""),
        )
        return cls(
            principles=principles,
            governance=governance,
            meta=meta,
            sections=sections,
        )
