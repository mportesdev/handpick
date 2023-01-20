"""
Handpick is a tool to traverse nested data structures and pick all
objects that meet certain criteria.
"""

from .core import (
    pick,
    Predicate,
    is_type,
    no_error,
    INT_STR,
    FLOAT_STR,
    NUM_STR,
    values_for_key,
    max_depth,
)

__version__ = "0.13.0"

__all__ = (
    "__version__",
    "pick",
    "Predicate",
    "is_type",
    "no_error",
    "INT_STR",
    "FLOAT_STR",
    "NUM_STR",
    "values_for_key",
    "max_depth",
)
