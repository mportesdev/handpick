"""
Handpick is a tool to traverse nested data structures recursively and
find all objects that meet certain criteria.
"""

from .core import (
    pick,
    Predicate,
    is_type,
    not_type,
    no_error,
    IS_COLLECTION,
    IS_MAPPING,
    INT_STR,
    FLOAT_STR,
    NUM_STR,
    values_for_key,
    max_depth,
)

__version__ = "0.11.0"

__all__ = (
    "__version__",
    "pick",
    "Predicate",
    "is_type",
    "not_type",
    "no_error",
    "IS_COLLECTION",
    "IS_MAPPING",
    "INT_STR",
    "FLOAT_STR",
    "NUM_STR",
    "values_for_key",
    "max_depth",
)
