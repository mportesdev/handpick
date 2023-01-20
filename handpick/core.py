from collections.abc import Iterable, Mapping

_ERRORS = (TypeError, ValueError, LookupError, AttributeError)


def pick(
    data,
    predicate=None,
    *,
    collections=True,
    dict_keys=False,
    strings=False,
    bytes_like=False,
):
    """Pick objects from `data` based on `predicate`.

    Traverse `data` recursively and yield all objects for which
    `predicate(obj)` is True or truthy. `data` should be an iterable
    collection.

    `predicate` must be callable, must take one argument, and should
    return a Boolean value. If `predicate` is omitted or None, all objects
    are picked.

    By default, collections of other objects are yielded just like any
    other objects. To exclude collections, pass `collections=False`.

    When traversing a mapping, only its values are inspected by default.
    To inspect both keys and values of mappings, pass `dict_keys=True`.

    By default, strings are not treated as collections of other objects
    and therefore not iterated by the recursive algorithm. This can be
    changed by passing `strings=True`. Empty strings and strings of
    length 1 are never iterated.

    By default, bytes-like sequences (bytes and bytearrays) are not
    treated as collections of other objects and therefore not iterated
    by the recursive algorithm. This can be changed by passing
    `bytes_like=True`.
    """
    if predicate is None:
        predicate = _default_predicate
    if not callable(predicate):
        raise TypeError("predicate must be callable")
    if not _is_collection(data, strings, bytes_like):
        return

    is_mapping = _is_mapping(data)
    for obj in data:
        if is_mapping:
            # (key, value) or just (value,)
            obj = (obj, data[obj]) if dict_keys else (data[obj],)
        elif collections or not _is_collection(obj, strings, bytes_like):
            # test object against predicate
            if predicate(obj):
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


def _default_predicate(_):
    return True


def _is_collection(obj, strings=False, bytes_like=False):
    return all(
        (
            isinstance(obj, Iterable),
            not isinstance(obj, str) or (strings and len(obj) > 1),
            not isinstance(obj, (bytes, bytearray)) or bytes_like,
        )
    )


def _is_mapping(obj):
    return isinstance(obj, Mapping)


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

    def __and__(self, other):
        """Override the `&` operator."""

        if not callable(other):
            return NotImplemented
        if isinstance(other, type(self)):
            other = other.func

        def fn(obj):
            return self.func(obj) and other(obj)

        return type(self)(fn)

    __rand__ = __and__

    def __or__(self, other):
        """Override the `|` operator."""

        if not callable(other):
            return NotImplemented
        if isinstance(other, type(self)):
            other = other.func

        def fn(obj):
            return self.func(obj) or other(obj)

        return type(self)(fn)

    __ror__ = __or__

    def __invert__(self):
        """Override the `~` operator."""

        def fn(obj):
            return not self.func(obj)

        return type(self)(fn)


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

    for mapping in pick([data], _is_mapping):
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
    if not _is_collection(data):
        return

    yield depth

    is_mapping = _is_mapping(data)
    for obj in data:
        if is_mapping:
            # switch from key to value and proceed
            obj = data[obj]
        yield from _iter_depth(obj, depth=depth + 1)
