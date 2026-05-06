from dataclasses import dataclass, field

from byte.support.utils import list_to_multiline_text


@dataclass
class ConstitutionPrinciple:
    """A single named principle within the Core Principles section."""

    name: str
    description: str


@dataclass
class ConstitutionSection:
    """An arbitrary additional section (beyond Core Principles and Governance)."""

    name: str
    content: str
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
        principles:    ordered list of Core Principles
        governance:    free-text governance rules
        meta:          version / ratification info

    Optional fields:
        sections:  any additional named sections (e.g. "Security Requirements")
    """

    project_name: str
    principles: list[ConstitutionPrinciple]
    governance: str
    meta: ConstitutionMeta
    sections: list[ConstitutionSection] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "principles": [{"name": p.name, "description": p.description} for p in self.principles],
            "governance": self.governance,
            "meta": {
                "version": self.meta.version,
                "ratified": self.meta.ratified,
                "last_amended": self.meta.last_amended,
            },
            "sections": [
                {
                    "name": s.name,
                    "content": s.content,
                    **({} if s.applies_to is None else {"applies_to": s.applies_to}),
                }
                for s in self.sections
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
        for principle in self.principles:
            lines.append(f"### {principle.name}")
            lines.append("")
            lines.append(principle.description)
            lines.append("")

        # Additional sections (each may be scoped to specific file patterns)
        for section in self.sections:
            lines.append(f"## {section.name}")
            lines.append("")
            if section.applies_to:
                scopes = ", ".join(f"`{p}`" for p in section.applies_to)
                lines.append(f"*Applies to: {scopes}*")
                lines.append("")
            lines.append(section.content)
            lines.append("")

        # Governance
        lines.append("## Governance")
        lines.append("")
        lines.append(self.governance)
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
        principles = [
            ConstitutionPrinciple(name=p["name"], description=p["description"]) for p in data.get("principles", [])
        ]
        sections = [
            ConstitutionSection(
                name=s["name"],
                content=s["content"],
                applies_to=s.get("applies_to"),
            )
            for s in data.get("sections", [])
        ]
        raw_meta = data.get("meta", {})
        meta = ConstitutionMeta(
            version=raw_meta.get("version", "0.0.1"),
            ratified=raw_meta.get("ratified", ""),
            last_amended=raw_meta.get("last_amended", ""),
        )
        return cls(
            project_name=data.get("project_name", ""),
            principles=principles,
            governance=data.get("governance", ""),
            meta=meta,
            sections=sections,
        )
