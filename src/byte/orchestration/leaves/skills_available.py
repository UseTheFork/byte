from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.skills import SkillLoaderService
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class SkillsAvailable(Leaf):
    def __init__(self, has_section: bool = False):
        self.has_section = has_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        skill_loader_service = prompt_assembler.get_app().make(SkillLoaderService)

        skills_xml = skill_loader_service.skills_to_prompt_xml(skill_loader_service.skills)

        if not skills_xml:
            return list_to_multiline_text(
                [
                    Section.start(SectionType.AVALIABLE_SKILLS),
                    "```",
                    "NO skills avaliable.",
                    "```",
                ]
            )

        message_parts = [
            Section.start(SectionType.AVALIABLE_SKILLS),
            "```",
            skills_xml,
            "```",
            Section.sub_heading("Skills Usage", 2),
            f"The `{Boundary.open(BoundaryType.DESCRIPTION)}` of each skill is a TRIGGER — it tells you *when* a skill applies. It is NOT a specification of what the skill does or how to do it. The procedure, scripts, commands, references, and required flags live only in the SKILL.md body. You do not know what a skill actually does until you have read its SKILL.md.",
            "",
            "MANDATORY activation flow:",
            f"1. Scan `{Boundary.open(BoundaryType.AVAILABLE_SKILLS)}` against the current user task.",
            # f"2. If any skill's `{Boundary.open(BoundaryType.DESCRIPTION)}` matches, call the `{SelectHarnessSkillsTool.name}` with its `{Boundary.open(BoundaryType.NAME)}` EXACTLY as shown.",
            Section.end(),
        ]

        return list_to_multiline_text(message_parts)
