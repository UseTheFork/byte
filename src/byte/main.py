import asyncio
import sys
from pathlib import Path

from pydantic import ValidationError

from byte.agent import AgentServiceProvider
from byte.analytics import AnalyticsProvider
from byte.cli import CLIServiceProvider
from byte.clipboard import ClipboardServiceProvider
from byte.code_operations import PromptFormatProvider
from byte.development import DevelopmentServiceProvider
from byte.files import FileServiceProvider
from byte.foundation import Application
from byte.git import GitServiceProvider
from byte.knowledge import KnowledgeServiceProvider
from byte.lint import LintServiceProvider
from byte.llm import LLMServiceProvider
from byte.lsp import LSPServiceProvider
from byte.memory import MemoryServiceProvider
from byte.presets import PresetsProvider
from byte.system import SystemServiceProvider
from byte.web import WebServiceProvider

PROVIDERS = [
    CLIServiceProvider,
    MemoryServiceProvider,
    KnowledgeServiceProvider,
    FileServiceProvider,
    # ToolsServiceProvider,
    LLMServiceProvider,
    GitServiceProvider,
    LintServiceProvider,
    AgentServiceProvider,
    LSPServiceProvider,
    AnalyticsProvider,
    PromptFormatProvider,
    WebServiceProvider,
    PresetsProvider,
    ClipboardServiceProvider,
    DevelopmentServiceProvider,
    SystemServiceProvider,
]


def cli():
    """Byte CLI Assistant"""

    try:
        application = Application.configure(Path.cwd(), PROVIDERS).create()

    except ValidationError:
        raise

    asyncio.run(application.handle_command(sys.argv))


if __name__ == "__main__":
    cli()
