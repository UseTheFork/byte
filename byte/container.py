from typing import Any, Callable, Dict


class Container:
    def __init__(self):
        self._bindings: Dict[str, Callable] = {}
        self._instances: Dict[str, Any] = {}

    def bind(self, abstract: str, concrete: Callable):
        self._bindings[abstract] = concrete

    def singleton(self, abstract: str, concrete: Callable):
        self._bindings[abstract] = concrete
        # Mark as singleton somehow

    def make(self, abstract: str):
        if abstract in self._instances:
            return self._instances[abstract]

        if abstract in self._bindings:
            instance = self._bindings[abstract]()
            self._instances[abstract] = instance
            return instance

        raise ValueError(f"No binding found for {abstract}")


# Global container
app = Container()
