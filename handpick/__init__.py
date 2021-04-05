"""
Handpick is a tool to traverse nested data structures recursively and
find all objects that meet certain criteria.
"""

from .core import pick, predicate, NO_CONTAINERS, NO_LIST_DICT

__version__ = '0.5.0'

__all__ = ['__version__', 'pick', 'predicate', 'NO_CONTAINERS', 'NO_LIST_DICT']
