|tests| |coverage| |release| |license| |pyversions| |format| |downloads|

========
Handpick
========

Handpick is a tool to traverse nested data structures and pick all
objects that meet certain criteria.


The ``pick`` function
=====================

The ``pick`` generator function is the library's main component.
It performs the recursive traversal of a (presumably nested) data
structure and applies the picking criteria provided in the form of a
predicate function (see below for various examples). Picked objects are
retrieved lazily by an iterator.


Simple predicate functions
--------------------------

The predicate function is passed to ``pick`` as the second positional
argument. In simple cases, you can use a lambda function as a
predicate. For example:

.. code-block:: python

    from handpick import pick

    data = [[1, 'Py'], [-2, ['', 3.0]], -4]

    non_empty_strings = pick(data, lambda s: isinstance(s, str) and s)

.. code::

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


Suppressing errors
------------------

One important thing to note: when a call to the predicate function
raises an exception, it is simply assumed that the object in question
does not meet the picking criteria, and the exception is suppressed.
For example:

.. code-block:: python

    from handpick import pick

    def above_zero(n):
        return n > 0

    data = [[1, 'Py'], [-2, ['', 3.0]], -4]

    positive_numbers = pick(data, above_zero)

.. code::

    >>> list(positive_numbers)
    [1, 3.0]

In the example above, several lists and strings were internally passed
to the ``above_zero`` function but no ``TypeError`` propagated up to
the code that called ``pick``.


Handling dictionary keys
------------------------

When inspecting dictionaries or other mappings, you can configure
whether or not ``pick`` will inspect dictionary keys using the
``dict_keys`` keyword argument. Default is False, which means only
dictionary values are inspected. For example:

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

The ``predicate`` decorator wraps a function in an object that can be
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


Predicate factories
-------------------

The ``is_type`` and ``not_type`` functions can be used to create
predicates based on an object's type. For example:

.. code-block:: python

    from handpick import pick, is_type, not_type

    data = [[1.0, [2, True]], [False, [3]], ['4', {5, True}]]

    strictly_integers = pick(data, is_type(int) & not_type(bool))

.. code::

    >>> list(strictly_integers)
    [2, 3, 5]


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

**Note:** Despite being iterable, strings and bytes-like objects are
not regarded as containers of other objects by ``NO_CONTAINERS``.


Useful functions
================


The ``values_for_key`` function
-------------------------------

When inspecting data structures that contain dictionaries or other
mappings, you can use this function to retrieve values associated with
a specific key, regardless of the nested depth in which these values
are stored. Values are retrieved lazily by an iterator. For example:

.. code-block:: python

    from handpick import values_for_key

    data = {'node_id': 4,
            'child_nodes': [{'node_id': 8,
                             'child_nodes': [{'node_id': 16}]},
                            {'node_id': 9}]}

    node_ids = values_for_key(data, key='node_id')

.. code::

    >>> list(node_ids)
    [4, 8, 16, 9]


The ``flat`` function
---------------------

This function can be used to flatten a nested data structure. Values
are retrieved lazily by an iterator. For example:

.. code-block:: python

    from handpick import flat

    data = [[], [0], [[[], 1], [2, [3, [4]], []], [5]]]
    flat_data = flat(data)

.. code::

    >>> list(flat_data)
    [0, 1, 2, 3, 4, 5]

When flattening dictionaries or other mappings, only its values are
inspected. For example:

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

**Note:** Just like non-empty containers, empty containers constitute
another level of nested depth. For example:

.. code::

    >>> max_depth([0, [1, []]])
    2


API reference
=============

handpick.pick(data, predicate, dict_keys=False, strings=False, bytes_like=False)
    Pick objects from ``data`` based on ``predicate``.

    Traverse ``data`` recursively and yield all objects for which
    ``predicate(obj)`` is True or truthy.

    ``data`` should be an iterable container.

    ``predicate`` should be a callable taking one argument and returning
    a Boolean value. If ``predicate`` is not callable, equality will be
    used as the picking criteria, i.e. objects for which
    ``obj == predicate`` will be yielded.

    When traversing a mapping, only its values are inspected by
    default. If ``dict_keys`` is set to True, both keys and values of the
    mapping are inspected.

    By default, strings are not regarded as containers of other objects
    and therefore not iterated by the recursive algorithm. This can be
    changed by setting ``strings`` to True. Strings of length 1 are never
    iterated.

    By default, bytes-like sequences (bytes and bytearrays) are not
    regarded as containers of other objects and therefore not iterated
    by the recursive algorithm. This can be changed by setting
    ``bytes_like`` to True.

@handpick.predicate(func)
    Decorator wrapping a function in a predicate object.

    The decorated function can be combined with other predicates using
    the operators ``&`` (and) and ``|`` (or), as well as negated using the
    operator ``~`` (not).

    Predicate objects are intended to be used as the ``predicate``
    argument to the ``pick`` function.

handpick.is_type(type_or_types)
    Predicate factory. Return a predicate that returns True if
    object is an instance of specified type(s).

    ``type_or_types`` must be a type or tuple of types.

handpick.not_type(type_or_types)
    Predicate factory. Return a predicate that returns True if
    object is not an instance of specified type(s).

    ``type_or_types`` must be a type or tuple of types.

handpick.ALL
    Predicate that returns True for all objects.

handpick.NO_CONTAINERS
    Predicate that returns True for non-iterable objects, strings
    and bytes-like objects.

handpick.values_for_key(data, key)
    Pick values associated with a specific key.

    Traverse ``data`` recursively and yield a sequence of dictionary
    values that are mapped to a dictionary key ``key``.

handpick.flat(data)
    Flatten ``data``.

    Yield a sequence of objects from a (presumably nested) data
    structure ``data``. Only non-iterable objects, strings and bytes-like
    objects are yielded.

    When traversing a mapping, only its values are inspected.

handpick.max_depth(data)
    Return maximum nested depth of ``data``.

    ``data`` should be an iterable container. Depth is counted from zero,
    i.e. the direct elements of ``data`` are in depth 0.


.. |tests| image:: https://github.com/mportesdev/handpick/actions/workflows/tests.yml/badge.svg
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
