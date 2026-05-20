from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.skills import SkillLoaderService
from byte.support import Boundary, BoundaryType, Section, SectionType
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class SkillsLoaded(Leaf):
    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        app = prompt_assembler.get_app()
        harness = prompt_assembler.get_state().get("harness", [])
        skill_loader_service = prompt_assembler.get_app().make(SkillLoaderService)

        skill_names: list[str] = harness.get("skills", [])
        app["log"].info(skill_names)

        loaded_skills = {}
        for name in skill_names:
            skill = skill_loader_service.get_skill(name)
            if skill is not None:
                loaded_skills[name] = skill

        app["log"].info(loaded_skills)

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
