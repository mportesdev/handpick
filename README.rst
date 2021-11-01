|build| |coverage| |version| |pyversions| |license| |format| |downloads|

========
Handpick
========

Handpick is a tool to traverse nested data structures and pick all
objects that meet certain criteria.


Installation
============

.. code::

    pip install handpick


Quick introduction
==================


The ``pick`` function
---------------------

The ``pick`` generator function performs the recursive traversal of a
(presumably nested) data structure and applies the picking criteria provided
in the form of a predicate function (see below for various examples). Picked
objects are retrieved lazily by an iterator.


Simple predicate functions
~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~

When inspecting dictionaries or other mappings, you can configure
whether or not ``pick`` will inspect dictionary keys using the
``dict_keys`` keyword argument. Default is False, which means only
dictionary values are inspected. For example:

.. code-block:: python

    from handpick import pick

    data = {'foo': {'name': 'foo'}, 'bar': {'name': 'bar'}}

    default = pick(data, lambda s: 'a' in s)
    keys_included = pick(data, lambda s: 'a' in s, dict_keys=True)

.. code::

    >>> list(default)
    ['bar']
    >>> list(keys_included)
    ['name', 'bar', 'name', 'bar']


Predicates
----------


The ``Predicate`` decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``Predicate`` decorator wraps a function in an object that can be
combined with other predicates using the operators ``&`` (and) and
``|`` (or), as well as negated using the operator ``~`` (not).


Combining predicates
~~~~~~~~~~~~~~~~~~~~

For example:

.. code-block:: python

    from handpick import pick, Predicate

    @Predicate
    def is_int(n):
        return isinstance(n, int)

    @Predicate
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition, the ``&`` and ``|`` operations are supported between
predicates and regular undecorated functions. For example:

.. code-block:: python

    from handpick import pick, Predicate

    @Predicate
    def is_list(obj):
        return isinstance(obj, list)

    data = [('1', [2]), {('x',): [(3, [4]), '5']}, ['x', ['6']], {7: ('x',)}]

    # compound predicate
    short_list = (lambda obj: len(obj) < 2) & is_list

    short_lists = pick(data, short_list)

.. code::

    >>> list(short_lists)
    [[2], [4], ['6']]


Suppressing errors
~~~~~~~~~~~~~~~~~~

One important thing to note: when the predicate's underlying function raises
an exception, the exception is suppressed and instead the call to the predicate
returns False. In other words, it is assumed that the object in question does
not meet the picking criteria. For example:

.. code-block:: python

    from handpick import pick, Predicate

    @Predicate
    def above_zero(n):
        return n > 0

.. code::

    >>> above_zero(1)
    True
    >>> above_zero('a')
    False
    >>> positive_numbers = pick([[1, 'Py', -2], [None, 3.0]], above_zero)
    >>> list(positive_numbers)
    [1, 3.0]

In the example above, several lists and strings were internally compared to ``0``
but no ``TypeError`` propagated up to the code that called ``above_zero``.


Predicate factories
~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~

Handpick provides some predefined predicates to be used in common
scenarios. For example:

.. code-block:: python

    from handpick import pick, IS_COLLECTION

    data = [[], [0], [['1'], b'2']]

    # pick only objects that are not collections of other objects
    only_values = pick(data, ~IS_COLLECTION)

.. code::

    >>> list(only_values)
    [0, '1', b'2']

**Note:** Despite being iterable, strings and bytes-like objects are
not treated as collections of other objects by ``IS_COLLECTION``.

The same as above can be achieved by specifying the ``collections`` keyword
argument to ``pick``:

.. code::

    >>> only_values = pick(data, lambda obj: True, collections=False)
    >>> list(only_values)
    [0, '1', b'2']


Useful functions
----------------


The ``values_for_key`` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


The ``max_depth`` function
~~~~~~~~~~~~~~~~~~~~~~~~~~

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

**Note:** Just like non-empty collections, empty collections constitute
another level of nested depth. For example:

.. code::

    >>> max_depth([0, [1, []]])
    2


Recipes
=======


Flattening nested data
----------------------

For example:

.. code-block:: python

    from handpick import pick, not_type

    data = [[], [0], [[[], 1], [2, [3, [4]], []], [5]]]
    flat_data = pick(data, not_type(list))

.. code::

    >>> list(flat_data)
    [0, 1, 2, 3, 4, 5]


API reference
=============

pick
----

*handpick.pick(data, predicate, collections=True, dict_keys=False, strings=False, bytes_like=False)*

Pick objects from ``data`` based on ``predicate``.

Traverse ``data`` recursively and yield all objects for which
``predicate(obj)`` is True or truthy. ``data`` should be an iterable
collection. ``predicate`` should be a callable taking one argument
and returning a Boolean value.

If ``predicate`` is not callable, equality will be used as the picking
criteria, i.e. objects for which ``obj == predicate`` will be yielded.

By default, collections of other objects are yielded just like any
other objects. To exclude collections, pass ``collections=False``.

When traversing a mapping, only its values are inspected by default.
To inspect both keys and values of mappings, pass ``dict_keys=True``.

By default, strings are not treated as collections of other objects
and therefore not iterated by the recursive algorithm. This can be
changed by passing ``strings=True``. Strings of length 1 are never
iterated.

By default, bytes-like sequences (bytes and bytearrays) are not
treated as collections of other objects and therefore not iterated
by the recursive algorithm. This can be changed by passing
``bytes_like=True``.

Predicate
---------

*@handpick.Predicate(func)*

Decorator wrapping a function in a predicate object.

The decorated function can be combined with other predicates using
the operators ``&`` (and) and ``|`` (or), as well as negated using the
operator ``~`` (not).

Predicate objects are intended to be used as the ``predicate``
argument to the ``pick`` function.

is_type
-------

*handpick.is_type(type_or_types)*

Predicate factory. Return a predicate that returns True if
object is an instance of specified type(s).

``type_or_types`` must be a type or tuple of types.

not_type
--------

*handpick.not_type(type_or_types)*

Predicate factory. Return a predicate that returns True if
object is not an instance of specified type(s).

``type_or_types`` must be a type or tuple of types.

IS_COLLECTION
-------------

*handpick.IS_COLLECTION*

Predicate that returns True for iterable collections of other
objects. Strings and bytes-like objects are not treated as collections.

IS_MAPPING
----------

*handpick.IS_MAPPING*

Predicate that returns True for dictionaries and other mappings.

values_for_key
--------------

*handpick.values_for_key(data, key)*

Pick values associated with a specific key.

Traverse ``data`` recursively and yield a sequence of dictionary
values that are mapped to ``key``. ``key`` may be a list of multiple
keys.

max_depth
---------

*handpick.max_depth(data)*

Return maximum nested depth of ``data``.

``data`` should be an iterable collection. Depth is counted from zero,
i.e. the direct elements of ``data`` are in depth 0.


.. |build| image:: https://github.com/mportesdev/handpick/actions/workflows/build-test.yml/badge.svg
    :target: https://github.com/mportesdev/handpick/actions
.. |coverage| image:: https://img.shields.io/codecov/c/gh/mportesdev/handpick
    :target: https://codecov.io/gh/mportesdev/handpick
.. |version| image:: https://img.shields.io/pypi/v/handpick
    :target: https://pypi.org/project/handpick
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/handpick
    :target: https://pypi.org/project/handpick
.. |license| image:: https://img.shields.io/github/license/mportesdev/handpick
    :target: https://github.com/mportesdev/handpick/blob/main/LICENSE
.. |format| image:: https://img.shields.io/pypi/format/handpick
    :target: https://pypi.org/project/handpick/#files
.. |downloads| image:: https://pepy.tech/badge/handpick
    :target: https://pepy.tech/project/handpick
