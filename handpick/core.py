"""
Handpick is a tool to inspect nested data structures recursively and
find all objects that meet certain criteria.
"""

from collections.abc import Mapping, Iterable

_ERRORS = (TypeError, ValueError, IndexError, KeyError, AttributeError)


def pick(root, predicate, dict_keys=False, strings=False, bytes_like=False):
    """Yield all objects recursively from `root` for which
    `predicate(obj)` is true.

    `root` should be an iterable container. `predicate` should be a
    callable taking one object as argument and returning a Boolean
    value. If `predicate` is not callable, equality will be used as the
    picking criteria, i.e. objects for which `obj == predicate` is true
    will be yielded.

    When traversing a mapping, only its values are inspected by
    default. If `dict_keys` is set to True, both keys and values of the
    mapping are inspected.

    By default, strings are not considered containers and therefore not
    visited by the recursive algorithm. This can be changed by setting
    `strings` to True. Strings of length 0 or 1 are never visited.

    By default, bytes-like sequences (bytes and bytearrays) are not
    considered containers and therefore not visited by the recursive
    algorithm. This can be changed by setting `bytes_like` to True.
    """
    if not isinstance(root, Iterable):
        return
    if isinstance(root, str) and (not strings or len(root) <= 1):
        return
    if isinstance(root, (bytes, bytearray)) and not bytes_like:
        return

    root_is_mapping = isinstance(root, Mapping)
    predicate_callable = callable(predicate)
    for obj in root:
        if root_is_mapping:
            if dict_keys:
                # process key
                yield from pick([obj], predicate,
                                dict_keys, strings, bytes_like)
            # switch from key to value and proceed
            obj = root[obj]
        if predicate_callable:
            try:
                if predicate(obj):
                    yield obj
            except _ERRORS:
                # exception indicates that object does not meet predicate
                pass
        elif obj == predicate:
            yield obj
        yield from pick(obj, predicate, dict_keys, strings, bytes_like)


def predicate(func):
    """Decorator wrapping a function with a predicate object.

    The decorated function can be combined with other predicates using
    the operators `&` (and), `|` (or) and `~` (not). The resulting
    object can be passed as the `predicate` argument to `pick`.
    """
    return _Predicate(func)


class _Predicate:
    def __init__(self, func):
        self.func = func

    def __call__(self, obj):
        return self.func(obj)

    def __and__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        def _and(obj):
            return self.func(obj) and other.func(obj)

        return self.__class__(_and)

    def __or__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        def _or(obj):
            return self.func(obj) or other.func(obj)

        return self.__class__(_or)

    def __invert__(self):
        def _not(obj):
            return not self.func(obj)

        return self.__class__(_not)
