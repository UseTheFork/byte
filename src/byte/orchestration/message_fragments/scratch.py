from typing import TYPE_CHECKING, List, override

from langchain_core.messages import BaseMessage, ToolMessage

from byte.orchestration import MessageFragment

if TYPE_CHECKING:
    from byte.orchestration import PromptAssembler


class Scratch(MessageFragment):
    @override
    async def assemble(self, prompt_assembler: PromptAssembler) -> List[BaseMessage]:
        scratch_state = prompt_assembler.generate_scratch_state()

        last_tool_idx = next(
            (len(scratch_state) - 1 - i for i, m in enumerate(reversed(scratch_state)) if isinstance(m, ToolMessage)),
            None,
        )

        def _strip_cache_control(content: list | str) -> list:
            if isinstance(content, str):
                return [{"type": "text", "text": content}]
            return [{k: v for k, v in block.items() if k != "cache_control"} for block in content]

        rebuilt: list[BaseMessage] = []
        for i, msg in enumerate(scratch_state):
            if isinstance(msg, ToolMessage):
                clean_content = _strip_cache_control(msg.content)
                if i == last_tool_idx and clean_content:
                    clean_content[-1] = {**clean_content[-1], "cache_control": {"type": "ephemeral"}}
                rebuilt.append(ToolMessage(content=clean_content, tool_call_id=msg.tool_call_id, name=msg.name))
            else:
                rebuilt.append(msg)
        scratch_state = rebuilt

        return scratch_state
