from typing import List, Type

from byte.harness import BootstrapAgentTool
from byte.support import ServiceProvider
from byte.tools import BaseTool


class HarnessServiceProvider(ServiceProvider):
    def tools(self) -> List[Type[BaseTool]]:
        return [
            BootstrapAgentTool,
        ]
