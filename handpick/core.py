"""
Handpick is a tool to inspect nested data structures recursively and
find all objects that meet certain criteria.
"""

from collections.abc import Mapping, Iterable


def pick(root, predicate, dict_keys=False, strings=False, bytes_like=False):
    if not isinstance(root, Iterable):
        return
    if isinstance(root, str) and (not strings or len(root) <= 1):
        return
    if isinstance(root, (bytes, bytearray)) and not bytes_like:
        return

    is_mapping = isinstance(root, Mapping)
    for obj in root:
        if is_mapping:
            if dict_keys:
                # process key
                yield from pick([obj], predicate,
                                dict_keys, strings, bytes_like)
            # switch from key to value and proceed
            obj = root[obj]
        if callable(predicate):
            try:
                if predicate(obj):
                    yield obj
            except Exception:
                # exception indicates that object does not meet predicate
                pass
        elif obj == predicate:
            yield obj
        yield from pick(obj, predicate, dict_keys, strings, bytes_like)
