from typing import List, Type

from byte.support import ServiceProvider


class HarnessServiceProvider(ServiceProvider):
    def services(self) -> List[Type]:
        return []

    def commands(self) -> List[Type]:
        return []

    def tools(self) -> List[Type]:
        return []
