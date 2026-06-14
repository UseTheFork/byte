from typing import TYPE_CHECKING

from byte.orchestration import Leaf
from byte.skills import SkillLoaderService
from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class HarnessSkillsLoaded(Leaf):
    """Harness leaf that renders the skills loaded in the harness state."""

    async def assemble(self, prompt_assembler: PromptAssembler) -> str:
        harness = prompt_assembler.get_state().get("harness", {})
        skills_list = harness.get("skills", [])
        skill_loader_service = prompt_assembler.get_app().make(SkillLoaderService)

        lines = []

        for skill_name in skills_list:
            skill = skill_loader_service.get_skill(skill_name)
            if skill:
                lines.append(skill.to_markdown())

        if not lines:
            return ""

        return list_to_multiline_text(lines)
