"""
Handpick is a tool to traverse nested data structures recursively and
find all objects that meet certain criteria.
"""

from .core import (
    pick,
    predicate,
    is_type,
    not_type,
    NO_CONTAINERS,
    values_for_key,
    max_depth,
)

__version__ = '0.8.3'

__all__ = [
    '__version__', 'pick', 'predicate', 'is_type', 'not_type',
    'NO_CONTAINERS', 'values_for_key', 'max_depth'
]
