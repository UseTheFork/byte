import asyncio
import sys
from pathlib import Path

import uvloop
from pydantic import ValidationError

from byte.analytics import AnalyticsProvider
from byte.ask import AskServiceProvider
from byte.coder import CoderServiceProvider
from byte.command import CommandServiceProvider
from byte.constitution import ConstitutionServiceProvider
from byte.development import DevelopmentServiceProvider
from byte.event import EventsServiceProvider
from byte.files import FileServiceProvider
from byte.foundation import Application
from byte.git import GitServiceProvider
from byte.knowledge import KnowledgeServiceProvider
from byte.lint import LintServiceProvider
from byte.llm import LLMServiceProvider
from byte.lsp import LSPServiceProvider
from byte.memory import MemoryServiceProvider
from byte.node import NodeServiceProvider
from byte.orchestration import OrchestrationServiceProvider
from byte.skills import SkillsServiceProvider
from byte.specs import SpecsServiceProvider
from byte.system import SystemServiceProvider
from byte.tools import ToolsServiceProvider
from byte.tui import TUIServiceProvider
from byte.web import WebServiceProvider

PROVIDERS = [
    EventsServiceProvider,
    ToolsServiceProvider,
    CommandServiceProvider,
    GitServiceProvider,
    OrchestrationServiceProvider,
    # keep-sorted start
    AnalyticsProvider,
    AskServiceProvider,
    CoderServiceProvider,
    ConstitutionServiceProvider,
    SpecsServiceProvider,
    # PresetsProvider,
    DevelopmentServiceProvider,
    FileServiceProvider,
    KnowledgeServiceProvider,
    LLMServiceProvider,
    LSPServiceProvider,
    LintServiceProvider,
    MemoryServiceProvider,
    NodeServiceProvider,
    SkillsServiceProvider,
    SystemServiceProvider,
    TUIServiceProvider,
    WebServiceProvider,
    # keep-sorted end
]


def cli():
    """Byte CLI Assistant"""

    try:
        application = Application.configure(Path.cwd(), PROVIDERS).create()  # ty:ignore[invalid-argument-type]

    except ValidationError:
        raise

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  # ty:ignore[deprecated]
    asyncio.run(application.handle_command(sys.argv))


if __name__ == "__main__":
    cli()
