"""CLI domain for terminal interface and user interactions."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.domain.cli.argparse.base import ByteArgumentParser
    from byte.domain.cli.rich.markdown import CodeBlock, Heading, Markdown
    from byte.domain.cli.rich.menu import Menu, MenuInputHandler, MenuRenderer, MenuState, MenuStyle
    from byte.domain.cli.rich.panel_rule import PanelBottom, PanelTop
    from byte.domain.cli.rich.rune_spinner import RuneSpinner
    from byte.domain.cli.schemas import ByteTheme, SubprocessResult, ThemeRegistry
    from byte.domain.cli.service.command_registry import Command, CommandRegistry
    from byte.domain.cli.service.console_service import ConsoleService
    from byte.domain.cli.service.interactions_service import InteractionService
    from byte.domain.cli.service.prompt_toolkit_service import PromptToolkitService
    from byte.domain.cli.service.stream_rendering_service import StreamRenderingService
    from byte.domain.cli.service.subprocess_service import SubprocessService
    from byte.domain.cli.utils.formatters import MarkdownStream

__all__ = (
    "ByteArgumentParser",
    "ByteTheme",
    "CodeBlock",
    "Command",
    "CommandRegistry",
    "ConsoleService",
    "Heading",
    "InteractionService",
    "Markdown",
    "MarkdownStream",
    "Menu",
    "MenuInputHandler",
    "MenuRenderer",
    "MenuState",
    "MenuStyle",
    "PanelBottom",
    "PanelTop",
    "PromptToolkitService",
    "RuneSpinner",
    "StreamRenderingService",
    "SubprocessResult",
    "SubprocessService",
    "ThemeRegistry",
)

_dynamic_imports = {
    # keep-sorted start
    "ByteArgumentParser": "schemas",
    "ByteTheme": "cli.schemas",
    "CodeBlock": "rich.markdown",
    "Command": "service.command_registry",
    "CommandRegistry": "service.command_registry",
    "ConsoleService": "service.console_service",
    "Heading": "rich.markdown",
    "InteractionService": "service.interactions_service",
    "Markdown": "rich.markdown",
    "MarkdownStream": "utils.formatters",
    "Menu": "rich.menu",
    "MenuInputHandler": "rich.menu",
    "MenuRenderer": "rich.menu",
    "MenuState": "rich.menu",
    "MenuStyle": "rich.menu",
    "PanelBottom": "rich.panel_rule",
    "PanelTop": "rich.panel_rule",
    "PromptToolkitService": "service.prompt_toolkit_service",
    "RuneSpinner": "rich.rune_spinner",
    "StreamRenderingService": "service.stream_rendering_service",
    "SubprocessResult": "argparse.base",
    "SubprocessService": "service.subprocess_service",
    "ThemeRegistry": "cli.schemas",
    # keep-sorted end
}


def __getattr__(attr_name: str) -> object:
    module_name = _dynamic_imports.get(attr_name)
    parent = __spec__.parent if __spec__ is not None else None
    result = import_attr(attr_name, module_name, parent)
    globals()[attr_name] = result
    return result


def __dir__() -> list[str]:
    return list(__all__)
