import asyncio
import sys
from pathlib import Path

import uvloop
from pydantic import ValidationError

from byte.analytics import AnalyticsProvider
from byte.command import CommandServiceProvider
from byte.conventions.service_provider import ConventionsServiceProvider
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
from byte.skills.service_provider import SkillsServiceProvider
from byte.system import SystemServiceProvider
from byte.tools import ToolsServiceProvider
from byte.tui import TUIServiceProvider
from byte.web import WebServiceProvider
from byte.workflow import WorkflowServiceProvider

PROVIDERS = [
    EventsServiceProvider,
    CommandServiceProvider,
    ToolsServiceProvider,
    GitServiceProvider,
    SkillsServiceProvider,
    MemoryServiceProvider,
    KnowledgeServiceProvider,
    FileServiceProvider,
    ConventionsServiceProvider,
    LLMServiceProvider,
    LintServiceProvider,
    NodeServiceProvider,
    WorkflowServiceProvider,
    LSPServiceProvider,
    AnalyticsProvider,
    WebServiceProvider,
    # PresetsProvider,
    DevelopmentServiceProvider,
    SystemServiceProvider,
    TUIServiceProvider,
]


def cli():
    """Byte CLI Assistant"""

    try:
        application = Application.configure(Path.cwd(), PROVIDERS).create()

    except ValidationError:
        raise

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(application.handle_command(sys.argv))


if __name__ == "__main__":
    cli()
