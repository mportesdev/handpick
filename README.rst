|pytest| |coverage| |release| |license| |pyversions| |format| |downloads|

========
Handpick
========

Handpick is a tool to traverse nested data structures and pick all
objects that meet certain criteria.


The ``pick`` function
=====================

The ``pick`` generator function is the main component of the package.
It performs the recursive traversal of a (presumably nested) data
structure and applies the picking criteria provided in the form of a
predicate function (see below for various examples). Picked objects are
yielded lazily by a generator-iterator.


Simple predicate functions
--------------------------

The predicate function is passed to ``pick`` as the second positional
argument. In simple cases, lambda functions can be used as predicates.
For example:

.. code-block:: python

    from handpick import pick

    data = [[1, 'Py'], [2, ['', 3.0]], 4]

    two_or_more = pick(data, lambda n: n >= 2)
    non_empty_strings = pick(data, lambda s: isinstance(s, str) and s)

.. code::

    >>> list(two_or_more)
    [2, 3.0, 4]
    >>> list(non_empty_strings)
    ['Py']


Non-callable predicates
-----------------------

If ``predicate`` is not callable, equality will be used as the picking
criteria. For example:

.. code-block:: python

    from handpick import pick

    data = [1, [1.0, [2, 1.]], [{'1': 1}, [3]]]

    ones = pick(data, 1)    # equivalent to pick(data, lambda n: n == 1)

.. code::

    >>> list(ones)
    [1, 1.0, 1.0, 1]


Handling dictionary keys
------------------------

When inspecting mappings (dictionaries), you can configure whether or
not ``pick`` will inspect dictionary keys by specifying the
``dict_keys`` keyword argument. Default is False, which means only
values will be inspected. For example:

.. code-block:: python

    from handpick import pick

    data = {'key': {'name': 'foo'}, '_key': {'_name': '_bar'}}

    default = pick(data, lambda s: s.startswith('_'))
    keys_included = pick(data, lambda s: s.startswith('_'), dict_keys=True)

.. code::

    >>> list(default)
    ['_bar']
    >>> list(keys_included)
    ['_key', '_name', '_bar']


Predicates
==========


The ``predicate`` decorator
---------------------------

The ``predicate`` decorator wraps a function in a object that can be
combined with other predicates using the operators ``&`` (and) and
``|`` (or), as well as negated using the operator ``~`` (not).


Combining predicates
--------------------

For example:

.. code-block:: python

    from handpick import pick, predicate

    @predicate
    def is_int(n):
        return isinstance(n, int)

    @predicate
    def is_even(n):
        return n % 2 == 0

    data = [[4, [5.0, 1], 3.0], [[15, []], {17: [7, [8], 0]}]]

    # compound predicate
    non_even_int = is_int & ~is_even

    odd_integers = pick(data, non_even_int)

.. code::

    >>> list(odd_integers)
    [1, 15, 7]


Combining predicates with functions
-----------------------------------

In addition, the ``&`` and ``|`` operations are supported between
predicates and regular undecorated functions. For example:

.. code-block:: python

    from handpick import pick, predicate

    @predicate
    def is_list(obj):
        return isinstance(obj, list)

    data = [('1', [2]), {('x',): [(3, [4]), '5']}, ['x', ['6']], {7: ('x',)}]

    # compound predicate
    short_list = (lambda obj: len(obj) < 2) & is_list

    short_lists = pick(data, short_list)

.. code::

    >>> list(short_lists)
    [[2], [4], ['6']]


Built-in predicates
-------------------

Handpick provides some predefined predicates to be used in common
scenarios. For example:

.. code-block:: python

    from handpick import pick, ALL, NO_CONTAINERS

    data = [[], [0], [['1'], b'2']]

    # pick all objects encountered during recursive traversal of data
    everything = pick(data, ALL)

    # pick only objects that are not containers of other objects
    only_values = pick(data, NO_CONTAINERS)

.. code::

    >>> list(everything)
    [[], [0], 0, [['1'], b'2'], ['1'], '1', b'2']
    >>> list(only_values)
    [0, '1', b'2']

**Note:** Strings and bytes-like objects are not regarded as containers
of other objects by the ``NO_CONTAINERS`` built-in predicate.

Predicate factories
-------------------

The ``is_type`` and ``not_type`` functions can be used to create
predicates based on an object's type. For example:

.. code-block:: python

    from handpick import pick, is_type, not_type

    data = [[1.0, [2, True]], [False, [3]], ['4', {5, True}]]

    integers_only = pick(data, is_type(int) & not_type(bool))

.. code::

    >>> list(integers_only)
    [2, 3, 5]


Useful functions
================


The ``flat`` function
---------------------

This function can be used to flatten a nested data structure. For example:

.. code-block:: python

    from handpick import flat

    data = [[], [0], [[[], 1], [2, [3, [4]], []], [5]]]
    flat_data = flat(data)

.. code::

    >>> list(flat_data)
    [0, 1, 2, 3, 4, 5]

When flattening a mapping (dictionary), only its values are inspected.
For example:

.. code::

    >>> list(flat({1: 2, 3: {4: 5}}))
    [2, 5]

**Note:** ``flat(data)`` is a shortcut for ``pick(data, NO_CONTAINERS)``.


The ``max_depth`` function
--------------------------

This function returns the maximum nested depth of a data structure. For
example:

.. code-block:: python

    from handpick import max_depth

    nested_list = [0, [1, [2]]]
    nested_dict = {0: {1: {2: {3: {4: 4}}}}}

.. code::

    >>> max_depth(nested_list)
    2
    >>> max_depth(nested_dict)
    4

**Note:** Empty containers constitute a level of nested depth as well
as non-empty ones. For example:

.. code::

    >>> max_depth([0, [1, []]])
    2


API reference
=============

handpick.pick(data, predicate, dict_keys=False, strings=False, bytes_like=False)
    Pick objects from ``data`` based on ``predicate``.

    Traverse ``data`` recursively and yield all objects for which
    ``predicate(obj)`` is true.

    ``data`` should be an iterable container.

    ``predicate`` should be a callable taking one argument and returning
    a Boolean value. If ``predicate`` is not callable, equality will be
    used as the picking criteria, i.e. objects for which
    ``obj == predicate`` is true will be yielded.

    When traversing a mapping, only its values are inspected by
    default. If ``dict_keys`` is set to True, both keys and values of the
    mapping are inspected.

    By default, strings are not regarded as containers of other objects
    and therefore not visited by the recursive algorithm. This can be
    changed by setting ``strings`` to True. Strings of length 0 or 1 are
    never visited.

    By default, bytes-like sequences (bytes and bytearrays) are not
    regarded as containers of other objects and therefore not visited
    by the recursive algorithm. This can be changed by setting
    ``bytes_like`` to True.

@handpick.predicate(func)
    Decorator wrapping a function with a predicate object.

    The decorated function can be combined with other predicates using
    the operators ``&`` (and) and ``|`` (or), as well as negated using the
    operator ``~`` (not).

    Predicate objects are intended to be used as the ``predicate``
    argument to the ``pick`` function.

handpick.ALL
    Predicate that returns True for all objects.

handpick.NO_CONTAINERS
    Predicate that returns False for all iterable objects except
    strings and bytes-like objects.

handpick.NO_LIST_DICT
    Predicate that returns False for instances of ``list`` and
    ``dict``.

handpick.is_type(type_or_types)
    Predicate factory. Return a predicate that returns True if
    object is an instance of specified type(s).

    ``type_or_types`` must be a type or tuple of types.

handpick.not_type(type_or_types)
    Predicate factory. Return a predicate that returns True if
    object is not an instance of specified type(s).

    ``type_or_types`` must be a type or tuple of types.

handpick.flat(data)
    Flatten ``data``.

    Yield a sequence of objects from a (presumably nested) data
    structure ``data``. Only non-iterable objects, strings and bytes-like
    objects are yielded.

    When traversing a mapping, only its values are inspected.

handpick.max_depth(data)
    Return maximum nested depth of ``data``.

    ``data`` should be an iterable container. The depth of direct
    elements of ``data`` is 0.


.. |pytest| image:: https://github.com/mportesdev/handpick/workflows/pytest/badge.svg
    :target: https://github.com/mportesdev/handpick/actions
.. |coverage| image:: https://img.shields.io/codecov/c/gh/mportesdev/handpick
    :target: https://codecov.io/gh/mportesdev/handpick
.. |release| image:: https://img.shields.io/github/v/release/mportesdev/handpick
    :target: https://github.com/mportesdev/handpick/releases/latest
.. |license| image:: https://img.shields.io/github/license/mportesdev/handpick
    :target: https://github.com/mportesdev/handpick/blob/main/LICENSE
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/handpick
    :target: https://pypi.org/project/handpick
.. |format| image:: https://img.shields.io/pypi/format/handpick
    :target: https://pypi.org/project/handpick/#files
.. |downloads| image:: https://pepy.tech/badge/handpick
    :target: https://pepy.tech/project/handpick
