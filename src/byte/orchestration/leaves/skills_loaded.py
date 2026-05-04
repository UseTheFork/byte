from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.skills import SkillLoaderService
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class SkillsLoaded(Leaf):
    def __init__(self, has_section: bool = False):
        self.has_section = has_section

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        skill_loader_service = prompt_assembler.get_app().make(SkillLoaderService)

        loaded_skills = {name: skill for name, skill in skill_loader_service._skills.items() if not skill.active}
        if not loaded_skills:
            return ""

        message_parts = [
            Section.start(SectionType.SKILLS),
        ]

        for name, skill in loaded_skills.items():
            message_parts.extend(
                [
                    Boundary.open(BoundaryType.SKILL, meta={"name": name}),
                    skill.instructions,
                    Boundary.close(BoundaryType.SKILL),
                    "",
                ]
            )

        message_parts.extend(Section.end())

        return list_to_multiline_text(message_parts)
