|ukraine|

|version| |tests| |coverage| |pyversions| |pre-commit| |black| |bandit|

==========
 Handpick
==========

Handpick is a tool to work with nested data structures.


Installation
============

.. code::

    pip install handpick


Quick introduction
==================


The ``pick`` function
---------------------

The `pick`_ generator function performs the recursive traversal
of a nested data structure and picks all objects that meet certain
criteria provided in the form of a predicate function.
Picked objects are retrieved lazily by an iterator.


Simple predicate functions
~~~~~~~~~~~~~~~~~~~~~~~~~~

The predicate function is passed to ``pick`` as the ``predicate``
argument. For example:

.. code-block:: python

    from handpick import pick

    def is_non_empty_string(obj):
        return isinstance(obj, str) and obj

    data = [[1, ""], [-2, ["foo", 3.0]], -4, "bar"]

.. code::

    >>> for s in pick(data, predicate=is_non_empty_string):
    ...     print(s)
    ...
    foo
    bar


Handling dictionary keys
~~~~~~~~~~~~~~~~~~~~~~~~

When inspecting dictionaries or other mappings, you can configure
whether or not ``pick`` will inspect dictionary keys using the
``dict_keys`` keyword argument. Default is False, which means only
dictionary values are inspected. For example:

.. code-block:: python

    from handpick import pick

    data = {"foo": {"name": "foo"}, "bar": {"name": "bar"}}

.. code::

    >>> for s in pick(data, predicate=lambda obj: "a" in obj):
    ...     print(s)
    ...
    bar
    >>> for s in pick(data, predicate=lambda obj: "a" in obj, dict_keys=True):
    ...     print(s)
    ...
    name
    bar
    name
    bar


Predicates
----------


The ``Predicate`` decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `Predicate`_ decorator wraps a function in an object that can be
combined with other predicates using the operators ``&`` (and) and
``|`` (or), as well as negated using the operator ``~`` (not).


Combining predicates
~~~~~~~~~~~~~~~~~~~~

For example:

.. code-block:: python

    from handpick import pick, Predicate

    @Predicate
    def is_integer(obj):
        return isinstance(obj, int)

    @Predicate
    def is_even(number):
        return number % 2 == 0

    data = [[4, [5.0, 1], 3.0], [[15, []], {17: [7, [8], 0]}]]

    # compound predicate
    odd_int = is_integer & ~is_even

.. code::

    >>> for n in pick(data, predicate=odd_int):
    ...     print(n)
    ...
    1
    15
    7


Combining predicates with functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition, the ``&`` and ``|`` operations are supported between
predicates and regular undecorated functions. For example:

.. code-block:: python

    from handpick import pick, Predicate

    @Predicate
    def is_list(obj):
        return isinstance(obj, list)

    data = [("1", [2]), {("x",): [(3, [4]), "5"]}, ["x", ["6"]], {7: ("x",)}]

    # compound predicate
    short_list = (lambda obj: len(obj) < 2) & is_list

.. code::

    >>> for l in pick(data, predicate=short_list):
    ...     print(l)
    ...
    [2]
    [4]
    ['6']


Suppressing errors
~~~~~~~~~~~~~~~~~~

The important thing to note is that when the predicate's underlying
function raises an exception, the exception is suppressed and the predicate
returns False. In other words, it is assumed that the object in question does
not meet the picking criteria. For example:

.. code-block:: python

    from handpick import pick, Predicate

    @Predicate
    def above_zero(number):
        return number > 0

.. code::

    >>> above_zero(1)
    True
    >>> above_zero("a")
    False
    >>> for n in pick([[1, "Py", -2], [None, 3.0]], predicate=above_zero):
    ...     print(n)
    ...
    1
    3.0

In the example above, several lists and strings were internally compared to ``0``
but no ``TypeError`` propagated up to the code that called ``above_zero``.


Predicate factories
~~~~~~~~~~~~~~~~~~~

The `is_type`_ function can be used to create
predicates based on an object's type. For example:

.. code-block:: python

    from handpick import pick, is_type

    data = [[1.0, [2, True]], [False, [3]], ["4"]]

    strictly_int = is_type(int) & ~is_type(bool)

.. code::

    >>> for n in pick(data, predicate=strictly_int):
    ...     print(n)
    ...
    2
    3


Built-in predicates
~~~~~~~~~~~~~~~~~~~

Handpick provides some predefined predicates to be used in common
scenarios. For example:

.. code-block:: python

    from handpick import pick, NUM_STR

    data = {"id": "01353", "price": 15.42, "quantity": 68, "year": "2011"}

    # pick strings that can be cast to numbers
    numeric_strings = pick(data, predicate=NUM_STR)

.. code::

    >>> for s in numeric_strings:
    ...     print(s)
    ...
    01353
    2011


Useful functions
----------------


The ``values_for_key`` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When inspecting data structures that contain dictionaries or other
mappings, you can use `values_for_key`_ to retrieve values associated with
a specific key, regardless of the nested depth in which these values
are stored. Values are retrieved lazily by an iterator. For example:

.. code-block:: python

    from handpick import values_for_key

    data = {
        "node_id": 4,
        "child_nodes": [
            {
                "node_id": 8,
                "child_nodes": [
                    {
                        "node_id": 16,
                    },
                ],
            },
            {
                "id": 9,
            },
        ],
    }

.. code::

    >>> for i in values_for_key(data, key="node_id"):
    ...     print(i)
    ...
    4
    8
    16

Multiple keys may be specified at a time. For example:

.. code::

    >>> for i in values_for_key(data, key=["node_id", "id"]):
    ...     print(i)
    ...
    4
    8
    16
    9


The ``max_depth`` function
~~~~~~~~~~~~~~~~~~~~~~~~~~

This function returns the maximum nested depth of a data structure. For
example:

.. code::

    >>> from handpick import max_depth
    >>> max_depth([0, [1, [2]]])
    2
    >>> max_depth({0: {1: {2: {3: {4: 4}}}}})
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

Use the `pick`_ function, omitting the ``predicate`` argument and passing
``collections=False``. For example:

.. code-block:: python

    from handpick import pick

    data = [[], [0], [[[], 1], [2, [3, [4]], []], [5]]]

.. code::

    >>> list(pick(data, collections=False))
    [0, 1, 2, 3, 4, 5]


API reference
=============

pick
----

*handpick.pick(data, predicate=None, *, collections=True, dict_keys=False, strings=False, bytes_like=False)*

Pick objects from ``data`` based on ``predicate``.

Traverse ``data`` recursively and yield all objects for which
``predicate(obj)`` is True or truthy. ``data`` should be an iterable
collection.

``predicate`` must be callable, must take one argument, and should
return a Boolean value. If ``predicate`` is omitted or None, all objects
are picked.

By default, collections of other objects are yielded just like any
other objects. To exclude collections, pass ``collections=False``.

When traversing a mapping, only its values are inspected by default.
To inspect both keys and values of mappings, pass ``dict_keys=True``.

By default, strings are not treated as collections of other objects
and therefore not iterated by the recursive algorithm. This can be
changed by passing ``strings=True``. Empty strings and strings of
length 1 are never iterated.

By default, bytes-like sequences (bytes and bytearrays) are not
treated as collections of other objects and therefore not iterated
by the recursive algorithm. This can be changed by passing
``bytes_like=True``.

Predicate
---------

*@handpick.Predicate(func=None, *, suppressed_errors=(TypeError, ValueError, LookupError, AttributeError))*

Decorator wrapping a function in a predicate object.

The decorated function can be combined with other predicates using
the operators ``&`` (and) and ``|`` (or), as well as negated using the
operator ``~`` (not).

``suppressed_errors`` can be used to customize which exception classes
will be suppressed by the predicate.

Predicate objects are intended to be used as the ``predicate``
argument to the ``pick`` function.

is_type
-------

*handpick.is_type(type_or_types)*

Predicate factory. Return a predicate that returns True if
object is an instance of specified type(s).

``type_or_types`` must be a type or tuple of types.

no_error
--------

*handpick.no_error(func)*

Predicate factory. Return a predicate that returns True if ``func``
can be applied on object without an exception being raised,
False otherwise.

INT_STR
-------

*handpick.INT_STR*

Predicate that returns True for strings that can be converted
to int.

FLOAT_STR
---------

*handpick.FLOAT_STR*

Predicate that returns True for strings that can be converted
to float.

NUM_STR
-------

*handpick.NUM_STR*

Predicate that returns True for strings that can be converted
to a number (i.e. an int, float or complex).

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


.. |version| image:: https://img.shields.io/pypi/v/handpick
    :target: https://pypi.org/project/handpick
.. |ukraine| image:: https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg
    :target: https://stand-with-ukraine.pp.ua
.. |tests| image:: https://github.com/mportesdev/handpick/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/mportesdev/handpick/actions
.. |coverage| image:: https://img.shields.io/codecov/c/gh/mportesdev/handpick
    :target: https://codecov.io/gh/mportesdev/handpick
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/handpick
    :target: https://pypi.org/project/handpick
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
    :target: https://github.com/pre-commit/pre-commit
.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
.. |bandit| image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
