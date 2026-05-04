from byte.support import Boundary, BoundaryType
from byte.support.utils import list_to_multiline_text


def core_mandates(has_tools: bool = False) -> str:
    lines = [Boundary.open(BoundaryType.CORE_MANDATES)]

    if has_tools:
        lines.append(
            "- **Context Efficiency:** Be strategic in your use of the available tools to minimize unnecessary context usage while still providing the best answer that you can."
        )

    lines.append(Boundary.close(BoundaryType.CORE_MANDATES))

    return list_to_multiline_text(lines)
