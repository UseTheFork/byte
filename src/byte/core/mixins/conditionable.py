from typing import Any, Callable, Optional, TypeVar

from byte.core.utils import value

T = TypeVar("T")


class Conditionable:
    """Mixin that provides conditional execution capabilities.

    Enables classes to execute callbacks based on truthy/falsy conditions,
    supporting both static values and callable conditions with optional
    default fallback behavior.
    Usage: `instance.when(condition, lambda self: self.do_something())`
    """

    def when(
        self: T,
        condition: Any,
        callback: Callable[[T, Any], None],
        default: Optional[Callable[[T, Any], None]] = None,
    ) -> T:
        """Invoke a callable when a given value returns a truthy value.

        Usage: `store.when(True, lambda self, val: self.add("key", "value"))`
        """
        val = value(condition, self)

        if val:
            callback(self, val)
        elif default:
            default(self, val)

        return self

    def unless(
        self: T,
        condition: Any,
        callback: Callable[[T, Any], None],
        default: Optional[Callable[[T, Any], None]] = None,
    ) -> T:
        """Invoke a callable when a given value returns a falsy value.

        Usage: `store.unless(False, lambda self, val: self.add("key", "value"))`
        """
        val = value(condition, self)

        if not val:
            callback(self, val)
        elif default:
            default(self, val)

        return self
