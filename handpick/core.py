from collections.abc import Mapping, Iterable

_ERRORS = (TypeError, ValueError, IndexError, KeyError, AttributeError)


def pick(
    data, predicate, collections=True, dict_keys=False, strings=False, bytes_like=False
):
    """Pick objects from `data` based on `predicate`.

    Traverse `data` recursively and yield all objects for which
    `predicate(obj)` is True or truthy. `data` should be an iterable
    collection. `predicate` should be a callable taking one argument
    and returning a Boolean value.

    If `predicate` is not callable, equality will be used as the picking
    criteria, i.e. objects for which `obj == predicate` will be yielded.

    By default, collections of other objects are yielded just like any
    other objects. To exclude collections, pass `collections=False`.

    When traversing a mapping, only its values are inspected by default.
    To inspect both keys and values of mappings, pass `dict_keys=True`.

    By default, strings are not treated as collections of other objects
    and therefore not iterated by the recursive algorithm. This can be
    changed by passing `strings=True`. Strings of length 1 are never
    iterated.

    By default, bytes-like sequences (bytes and bytearrays) are not
    treated as collections of other objects and therefore not iterated
    by the recursive algorithm. This can be changed by passing
    `bytes_like=True`.
    """
    if not isinstance(data, Iterable):
        return
    if isinstance(data, str) and (not strings or len(data) == 1):
        return
    if isinstance(data, (bytes, bytearray)) and not bytes_like:
        return

    is_mapping = IS_MAPPING(data)
    predicate_callable = callable(predicate)
    for obj in data:
        if is_mapping:
            # (key, value) or just (value,)
            obj = (obj, data[obj]) if dict_keys else (data[obj],)
        elif collections or not IS_COLLECTION(obj):
            # test object against predicate
            if predicate_callable:
                if predicate(obj):
                    yield obj
            elif obj == predicate:
                yield obj
        # inspect object recursively
        yield from pick(obj, predicate, collections, dict_keys, strings, bytes_like)


class Predicate:
    """Decorator wrapping a function in a predicate object.

    The decorated function can be combined with other predicates using
    the operators `&` (and) and `|` (or), as well as negated using the
    operator `~` (not).

    Predicate objects are intended to be used as the `predicate`
    argument to the `pick` function.
    """

    def __init__(self, func):
        self.func = func

    def __call__(self, obj):
        try:
            return self.func(obj)
        except _ERRORS:
            # exception indicates that object does not meet predicate
            return False

    @classmethod
    def from_function(cls, func):
        return cls(func)

    def __and__(self, other):
        """Override the `&` operator."""

        if not callable(other):
            return NotImplemented
        if isinstance(other, self.__class__):
            other = other.func

        def fn(obj):
            return self.func(obj) and other(obj)

        return self.from_function(fn)

    def __rand__(self, other):
        return self & other

    def __or__(self, other):
        """Override the `|` operator."""

        if not callable(other):
            return NotImplemented
        if isinstance(other, self.__class__):
            other = other.func

        def fn(obj):
            return self.func(obj) or other(obj)

        return self.from_function(fn)

    def __ror__(self, other):
        return self | other

    def __invert__(self):
        """Override the `~` operator."""

        def fn(obj):
            return not self.func(obj)

        return self.from_function(fn)


# predicate factories


def is_type(type_or_types):
    """Predicate factory. Return a predicate that returns True if
    object is an instance of specified type(s).

    `type_or_types` must be a type or tuple of types.
    """

    @Predicate
    def new_predicate(obj):
        return isinstance(obj, type_or_types)

    return new_predicate


def not_type(type_or_types):
    """Predicate factory. Return a predicate that returns True if
    object is not an instance of specified type(s).

    `type_or_types` must be a type or tuple of types.
    """

    @Predicate
    def new_predicate(obj):
        return not isinstance(obj, type_or_types)

    return new_predicate


# built-in predicates

IS_COLLECTION = is_type(Iterable) & not_type((str, bytes, bytearray))
"""Predicate that returns True for iterable collections of other
objects. Strings and bytes-like objects are not treated as collections.
"""

IS_MAPPING = is_type(Mapping)
"""Predicate that returns True for dictionaries and other mappings."""


# useful functions


def values_for_key(data, key):
    """Pick values associated with a specific key.

    Traverse `data` recursively and yield a sequence of dictionary
    values that are mapped to `key`. `key` may be a list of multiple
    keys.
    """
    if not isinstance(key, list):
        key = [key]

    for mapping in pick([data], IS_MAPPING):
        for k in key:
            if k in mapping:
                yield mapping[k]


def max_depth(data):
    """Return maximum nested depth of `data`.

    `data` should be an iterable collection. Depth is counted from zero,
    i.e. the direct elements of `data` are in depth 0.
    """
    return max(_iter_depth(data), default=0)


def _iter_depth(data, depth=0):
    if not IS_COLLECTION(data):
        return

    yield depth

    is_mapping = IS_MAPPING(data)
    for obj in data:
        if is_mapping:
            # switch from key to value and proceed
            obj = data[obj]
        yield from _iter_depth(obj, depth=depth + 1)
