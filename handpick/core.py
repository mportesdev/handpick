from collections.abc import Mapping, Iterable

_ERRORS = (TypeError, ValueError, LookupError, AttributeError)


def pick(
    data,
    predicate=lambda obj: True,
    *,
    collections=True,
    dict_keys=False,
    strings=False,
    bytes_like=False,
):
    """Pick objects from `data` based on `predicate`.

    Traverse `data` recursively and yield all objects for which
    `predicate(obj)` is True or truthy. `data` should be an iterable
    collection. `predicate` should be a callable taking one argument
    and returning a Boolean value.

    If `predicate` is omitted, all objects are picked. If `predicate`
    is not callable, equality is used as criteria, i.e. objects for
    which `obj == predicate` are picked.

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
            test = predicate(obj) if predicate_callable else obj == predicate
            if test:
                yield obj
        # inspect object recursively
        yield from pick(
            obj,
            predicate,
            collections=collections,
            dict_keys=dict_keys,
            strings=strings,
            bytes_like=bytes_like,
        )


class Predicate:
    """Decorator wrapping a function in a predicate object.

    The decorated function can be combined with other predicates using
    the operators `&` (and) and `|` (or), as well as negated using the
    operator `~` (not).

    `suppressed_errors` can be used to customize which exception classes
    will be suppressed by the predicate.

    Predicate objects are intended to be used as the `predicate`
    argument to the `pick` function.
    """

    def __init__(self, func=None, *, suppressed_errors=_ERRORS):
        self.func = func
        self.suppressed_errors = suppressed_errors

    def __call__(self, obj):
        if self.func is None:
            # instance called as decorator
            self.func = obj
            return self
        try:
            # instance called as predicate
            return self.func(obj)
        except self.suppressed_errors:
            # exception indicates that object does not meet predicate
            return False

    @classmethod
    def from_function(cls, func):
        return cls(func)

    def __and__(self, other):
        """Override the `&` operator."""

        if not callable(other):
            return NotImplemented
        if isinstance(other, type(self)):
            other = other.func

        def fn(obj):
            return self.func(obj) and other(obj)

        return self.from_function(fn)

    __rand__ = __and__

    def __or__(self, other):
        """Override the `|` operator."""

        if not callable(other):
            return NotImplemented
        if isinstance(other, type(self)):
            other = other.func

        def fn(obj):
            return self.func(obj) or other(obj)

        return self.from_function(fn)

    __ror__ = __or__

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
    def pred(obj):
        return isinstance(obj, type_or_types)

    return pred


def not_type(type_or_types):
    """Predicate factory. Return a predicate that returns True if
    object is not an instance of specified type(s).

    `type_or_types` must be a type or tuple of types.
    """
    return ~is_type(type_or_types)


def _error(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as err:
        return err
    else:
        return None


def no_error(func):
    """Predicate factory. Return a predicate that returns True if `func`
    can be applied on object without an exception being raised,
    False otherwise.
    """

    @Predicate
    def pred(obj):
        return _error(func, obj) is None

    return pred


# built-in predicates

IS_COLLECTION = is_type(Iterable) & not_type((str, bytes, bytearray))
"""Predicate that returns True for iterable collections of other
objects. Strings and bytes-like objects are not treated as collections.
"""

IS_MAPPING = is_type(Mapping)
"""Predicate that returns True for dictionaries and other mappings."""

INT_STR = is_type(str) & no_error(int)
"""Predicate that returns True for strings that can be converted
to int."""

FLOAT_STR = is_type(str) & no_error(float)
"""Predicate that returns True for strings that can be converted
to float."""

NUM_STR = is_type(str) & no_error(complex)
"""Predicate that returns True for strings that can be converted
to a number (i.e. an int, float or complex)."""


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
