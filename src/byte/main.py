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
from byte.documentation import DocumentationServiceProvider
from byte.event import EventsServiceProvider
from byte.files import FileServiceProvider
from byte.foundation import Application
from byte.gateway import GatewayServiceProvider
from byte.git import GitServiceProvider
from byte.harness import HarnessServiceProvider
from byte.knowledge import KnowledgeServiceProvider
from byte.lint import LintServiceProvider
from byte.llm import LLMServiceProvider
from byte.memory import MemoryServiceProvider
from byte.node import NodeServiceProvider
from byte.orchestration import OrchestrationServiceProvider
from byte.research import ResearchServiceProvider
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
    GatewayServiceProvider,
    GitServiceProvider,
    OrchestrationServiceProvider,
    # keep-sorted start
    AnalyticsProvider,
    AskServiceProvider,
    CoderServiceProvider,
    ConstitutionServiceProvider,
    DevelopmentServiceProvider,
    DocumentationServiceProvider,
    FileServiceProvider,
    # PresetsProvider,
    HarnessServiceProvider,
    KnowledgeServiceProvider,
    LLMServiceProvider,
    # LSPServiceProvider,
    LintServiceProvider,
    MemoryServiceProvider,
    NodeServiceProvider,
    ResearchServiceProvider,
    SkillsServiceProvider,
    SpecsServiceProvider,
    SystemServiceProvider,
    TUIServiceProvider,
    WebServiceProvider,
    # keep-sorted end
]


def cli():
    """Configure and run the CLI application.

    Configures the Application with the current working directory and service providers,
    sets the asyncio event loop policy to uvloop, and runs the application's command
    handler with sys.argv.
    """
    try:
        application = Application.configure(Path.cwd(), PROVIDERS).create()  # ty:ignore[invalid-argument-type]

    except ValidationError:
        raise

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  # ty:ignore[deprecated]
    asyncio.run(application.handle_command(sys.argv))


if __name__ == "__main__":
    cli()
