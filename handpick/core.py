from collections.abc import Mapping, Iterable

_ERRORS = (TypeError, ValueError, IndexError, KeyError, AttributeError)


def pick(root, predicate, dict_keys=False, strings=False, bytes_like=False):
    """Pick objects from `root` based on `predicate`.

    Traverse `root` recursively and yield all objects for which
    `predicate(obj)` is true.

    `root` should be an iterable container.

    `predicate` should be a callable taking one argument and returning
    a Boolean value. If `predicate` is not callable, equality will be
    used as the picking criteria, i.e. objects for which
    `obj == predicate` is true will be yielded.

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
    the operators `&` (and) and `|` (or), as well as negated using the
    operator `~` (not).

    Predicate objects are intended to be used as the `predicate`
    argument to the `pick` function.
    """
    return _Predicate(func)


class _Predicate:
    def __init__(self, func):
        self.func = func

    def __call__(self, obj):
        return self.func(obj)

    def __and__(self, other):
        if not callable(other):
            return NotImplemented
        other_func = other.func if isinstance(other, self.__class__) else other

        def _and(obj):
            return self.func(obj) and other_func(obj)

        return self.__class__(_and)

    def __rand__(self, other):
        return self & other

    def __or__(self, other):
        if not callable(other):
            return NotImplemented
        other_func = other.func if isinstance(other, self.__class__) else other

        def _or(obj):
            return self.func(obj) or other_func(obj)

        return self.__class__(_or)

    def __ror__(self, other):
        return self | other

    def __invert__(self):
        def _not(obj):
            return not self.func(obj)

        return self.__class__(_not)


# built-in predicates

@predicate
def _all(obj):
    """Predicate that returns True for all objects."""

    return True


@predicate
def _no_containers(obj):
    """Predicate that returns False for all iterable objects except
    strings and bytes-like objects.
    """
    return not isinstance(obj, Iterable) \
        or isinstance(obj, (str, bytes, bytearray))


@predicate
def _no_list_dict(obj):
    """Predicate that returns False for instances of `list` and
    `dict`.
    """
    return not isinstance(obj, (list, dict))


ALL = _all
NO_CONTAINERS = _no_containers
NO_LIST_DICT = _no_list_dict


# predicate factories

def is_type(type_or_types):
    """Predicate factory. Return a predicate that returns True if
    object is an instance of specified type(s).

    `type_or_types` must be a type or tuple of types.
    """
    @predicate
    def _pred(obj):
        return isinstance(obj, type_or_types)

    return _pred


def not_type(type_or_types):
    """Predicate factory. Return a predicate that returns True if
    object is not an instance of specified type(s).

    `type_or_types` must be a type or tuple of types.
    """
    @predicate
    def _pred(obj):
        return not isinstance(obj, type_or_types)

    return _pred


# useful functions

def flat(data):
    """Flatten `data`.

    Yield a sequence of objects from a (presumably nested) data
    structure `data`. Only non-iterable objects, strings and bytes-like
    objects are yielded.

    When traversing a mapping, only its values are considered.
    """
    yield from pick(data, NO_CONTAINERS)


def max_depth(root):
    """Return maximum nested depth of `root`.

    `root` should be an iterable container. Direct elements of `root`
    are considered to be in depth 0. Empty containers do not constitute
    another level of nested depth.
    """
    return max(_iter_depth(root))


def _iter_depth(root, depth=0):
    if not isinstance(root, Iterable) \
            or isinstance(root, (str, bytes, bytearray)):
        return

    root_is_mapping = isinstance(root, Mapping)
    for obj in root:
        yield depth
        if root_is_mapping:
            # switch from key to value and proceed
            obj = root[obj]
        yield from _iter_depth(obj, depth=depth + 1)
