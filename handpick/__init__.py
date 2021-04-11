"""
Handpick is a tool to traverse nested data structures recursively and
find all objects that meet certain criteria.
"""

from .core import (
    pick,
    predicate,
    ALL,
    NO_CONTAINERS,
    NO_LIST_DICT,
    is_type,
    not_type,
    flat,
)

__version__ = '0.7.0'

__all__ = [
    '__version__', 'pick', 'predicate', 'ALL', 'NO_CONTAINERS', 'NO_LIST_DICT',
    'is_type', 'not_type', 'flat'
]
