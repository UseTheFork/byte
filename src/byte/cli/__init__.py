"""CLI domain for terminal interface and user interactions."""

from typing import TYPE_CHECKING

from byte._import_utils import import_attr

if TYPE_CHECKING:
    from byte.cli.argparse.base import ByteArgumentParser
    from byte.cli.rich.markdown import CodeBlock, Heading, Markdown
    from byte.cli.rich.menu import Menu, MenuInputHandler, MenuRenderer, MenuState, MenuStyle
    from byte.cli.rich.panel_rule import PanelBottom, PanelTop
    from byte.cli.rich.rune_spinner import RuneSpinner
    from byte.cli.schemas import ByteTheme, SubprocessResult, ThemeRegistry
    from byte.cli.service.command_registry import Command, CommandRegistry
    from byte.cli.service.interactions_service import InteractionService
    from byte.cli.service.prompt_toolkit_service import PromptToolkitService
    from byte.cli.service.stream_rendering_service import StreamRenderingService
    from byte.cli.service.subprocess_service import SubprocessService
    from byte.cli.service_provider import CLIServiceProvider
    from byte.cli.utils.formatters import MarkdownStream

__all__ = (
    "ByteArgumentParser",
    "ByteTheme",
    "CLIServiceProvider",
    "CodeBlock",
    "Command",
    "CommandRegistry",
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
    "ByteArgumentParser": "argparse.base",
    "ByteTheme": "schemas",
    "CLIServiceProvider": "service_provider",
    "CodeBlock": "rich.markdown",
    "Command": "service.command_registry",
    "CommandRegistry": "service.command_registry",
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
    "SubprocessResult": "schemas",
    "SubprocessService": "service.subprocess_service",
    "ThemeRegistry": "schemas",
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
