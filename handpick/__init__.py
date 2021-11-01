"""
Handpick is a tool to traverse nested data structures recursively and
find all objects that meet certain criteria.
"""

from .core import (
    pick,
    Predicate,
    is_type,
    not_type,
    IS_COLLECTION,
    IS_MAPPING,
    values_for_key,
    max_depth,
)

__version__ = "0.9.2"

__all__ = [
    "__version__",
    "pick",
    "Predicate",
    "is_type",
    "not_type",
    "IS_COLLECTION",
    "IS_MAPPING",
    "values_for_key",
    "max_depth",
]
