from typing import Any, Optional

from byte.core.mixins.conditionable import Conditionable


class ArrayStore(Conditionable):
    """Dictionary-based store with fluent interface and conditional execution.

    Provides a chainable API for managing key-value data with support for
    conditional operations, merging, and store manipulation. Extends Conditionable
    for when/unless conditional execution patterns.
    Usage: `store = ArrayStore({"key": "value"}).add("new", 42).when(True, ...)`
    """

    def __init__(self, data: Optional[dict[str, Any]] = None):
        """Initialize the array store with optional initial data.

        Usage: `store = ArrayStore({"initial": "data"})`
        """
        self._data: dict[str, Any] = data if data is not None else {}

    def add(self, key: str, val: Any) -> "ArrayStore":
        """Add an item to the store, evaluating callable values.

        Usage: `store.add("key", "value")` or `store.add("key", lambda: compute())`
        """
        self._data[key] = val
        return self

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a single item from the store with optional default.

        Usage: `val = store.get("key", "default_value")`
        """
        return self._data.get(key, default)

    def all(self) -> dict[str, Any]:
        """Retrieve all items in the store.

        Usage: `data = store.all()`
        """
        return self._data

    def is_not_empty(self) -> bool:
        """Determine if the store contains any items.

        Usage: `if store.is_not_empty(): ...`
        """
        return not self.is_empty()

    def is_empty(self) -> bool:
        """Determine if the store is empty.

        Usage: `if store.is_empty(): ...`
        """
        return len(self._data) == 0

    def merge(self, *arrays: dict[str, Any]) -> "ArrayStore":
        """Merge one or more dictionaries into the store.

        Usage: `store.merge({"key1": "val1"}, {"key2": "val2"})`
        """
        for array in arrays:
            self._data.update(array)
        return self

    def remove(self, key: str) -> "ArrayStore":
        """Remove an item from the store by key.

        Usage: `store.remove("unwanted_key")`
        """
        self._data.pop(key, None)
        return self

    def set(self, data: dict[str, Any]) -> "ArrayStore":
        """Overwrite the entire store with new data.

        Usage: `store.set({"new": "data"})`
        """
        self._data = data
        return self
