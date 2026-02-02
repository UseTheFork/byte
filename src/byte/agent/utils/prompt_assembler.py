from __future__ import annotations

import re
from typing import TYPE_CHECKING, TypeVar

from typing_extensions import List

from byte.support.utils import list_to_multiline_text

if TYPE_CHECKING:
    pass

T = TypeVar("T")


class PromptAssembler:
    def __init__(self, template: List[str] | None, **kwargs):
        if template is None or len(template) == 0:
            raise ValueError("template parameter is required and cannot be empty")

        self.template = template

    def assemble(self, **replacements) -> str:
        """Replace {placeholder} tokens in template with provided values.

        Automatically removes lines containing only placeholders that don't have corresponding values.
        Placeholders are expected to be on their own line with nothing else.

        Usage: `assembler.assemble(name="World", age=30)`
        """
        result_lines = []
        placeholder_pattern = r"^\{([^}]+)\}$"

        for line in self.template:
            match = re.match(placeholder_pattern, line)
            if match:
                # Line contains only a placeholder
                key = match.group(1)
                if key in replacements:
                    # Replace with the value
                    value = replacements[key]
                    result_lines.append(value if isinstance(value, str) else str(value))
                # If key not in replacements, skip this line (remove it)
            else:
                # Not a placeholder line, keep as-is
                result_lines.append(line)

        return list_to_multiline_text(result_lines)
