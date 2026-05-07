from dataclasses import dataclass, field

from byte.support.string import Str
from byte.support.utils import list_to_multiline_text


@dataclass
class ConstitutionPrinciple:
    """A single named principle within the Core Principles section."""

    name: str
    description: str


@dataclass
class ConstitutionItem:
    """A single named item within a ConstitutionSection.

    Using discrete items instead of a monolithic content string allows tools
    to perform surgical edits — only the targeted item's content needs to be
    replaced rather than the entire section blob.
    """

    name: str
    content: str


@dataclass
class ConstitutionGovernanceRule:
    """A single named governance rule within the Governance section.

    Keyed by slug in the parent dict for O(1) lookup and surgical edits.
    """

    name: str
    content: str


@dataclass
class ConstitutionSection:
    """An arbitrary additional section (beyond Core Principles and Governance).

    Attributes:
        name:       Section heading.
        items:      Named items keyed by item name for O(1) lookup and surgical edits.
        applies_to: Optional list of glob patterns (e.g. ["src/byte/node/**"]).
                    When None or empty, the section applies to all files.
    """

    name: str
    items: dict[str, ConstitutionItem] = field(default_factory=dict)
    applies_to: list[str] | None = None  # None = applies to all


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

    project_name: str
    principles: dict[str, ConstitutionPrinciple]
    governance: dict[str, ConstitutionGovernanceRule]
    meta: ConstitutionMeta
    sections: dict[str, ConstitutionSection] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "principles": [{"name": p.name, "description": p.description} for p in self.principles.values()],
            "governance": [{"name": r.name, "content": r.content} for r in self.governance.values()],
            "meta": {
                "version": self.meta.version,
                "ratified": self.meta.ratified,
                "last_amended": self.meta.last_amended,
            },
            "sections": [
                {
                    "name": s.name,
                    "items": [{"name": i.name, "content": i.content} for i in s.items.values()],
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
        lines.append(f"# {self.project_name} Constitution")
        lines.append("")

        # Core Principles
        lines.append("## Core Principles")
        lines.append("")
        for principle in self.principles.values():
            lines.append(f"### {principle.name}")
            lines.append("")
            lines.append(principle.description)
            lines.append("")

        # Additional sections (each may be scoped to specific file patterns)
        for section in self.sections.values():
            lines.append(f"## {section.name}")
            lines.append("")
            if section.applies_to:
                scopes = ", ".join(f"`{p}`" for p in section.applies_to)
                lines.append(f"*Applies to: {scopes}*")
                lines.append("")
            for item in section.items.values():
                lines.append(f"### {item.name}")
                lines.append("")
                lines.append(item.content)
                lines.append("")

        # Governance
        lines.append("## Governance")
        lines.append("")
        for rule in self.governance.values():
            lines.append(f"### {rule.name}")
            lines.append("")
            lines.append(rule.content)
            lines.append("")

        # Version footer
        lines.append(
            f"**Version**: {self.meta.version} | "
            f"**Ratified**: {self.meta.ratified} | "
            f"**Last Amended**: {self.meta.last_amended}"
        )

        return list_to_multiline_text(lines)

    @classmethod
    def from_dict(cls, data: dict) -> Constitution:
        principles: dict[str, ConstitutionPrinciple] = {}
        for p in data.get("principles", []):
            principle = ConstitutionPrinciple(name=p["name"], description=p["description"])
            principles[Str.slugify(principle.name)] = principle

        sections: dict[str, ConstitutionSection] = {}
        for s in data.get("sections", []):
            items: dict[str, ConstitutionItem] = {}
            for i in s.get("items", []):
                item = ConstitutionItem(name=i["name"], content=i["content"])
                items[Str.slugify(item.name)] = item

            section = ConstitutionSection(
                name=s["name"],
                items=items,
                applies_to=s.get("applies_to"),
            )
            sections[Str.slugify(section.name)] = section

        governance: dict[str, ConstitutionGovernanceRule] = {}
        for r in data.get("governance", []):
            rule = ConstitutionGovernanceRule(name=r["name"], content=r["content"])
            governance[Str.slugify(rule.name)] = rule

        raw_meta = data.get("meta", {})
        meta = ConstitutionMeta(
            version=raw_meta.get("version", "0.0.1"),
            ratified=raw_meta.get("ratified", ""),
            last_amended=raw_meta.get("last_amended", ""),
        )
        return cls(
            project_name=data.get("project_name", ""),
            principles=principles,
            governance=governance,
            meta=meta,
            sections=sections,
        )
