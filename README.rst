|pytest| |coverage| |release| |license| |pyversions| |format| |downloads|

Handpick is a tool to traverse nested data structures recursively and
find all objects that meet certain criteria.


The ``pick`` generator
----------------------

Simple predicate functions
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from handpick import pick

    root = [[1, 2, 100.0], [3, 'Py', [{}, 4], 5]]

    print(list(pick(root, lambda n: n > 3)))
    print(list(pick(root, lambda n: n > 3 and isinstance(n, int))))
    print(list(pick(root, lambda seq: len(seq) == 2)))

.. code::

    [100.0, 4, 5]
    [4, 5]
    ['Py', [{}, 4]]


Non-callable predicate
~~~~~~~~~~~~~~~~~~~~~~

This can be used e.g. to count occurrences of a value regardless of
the nested depth.

.. code-block:: python

    from handpick import pick

    root = [1, [1., [2, 1]], [{'id': 1, 'data': [0, 1.0]}, 1, [{}, [1]], 0]]

    ones = pick(root, 1)

.. code::

    >>> len(list(ones))
    7


Handling dictionary keys
~~~~~~~~~~~~~~~~~~~~~~~~

You can configure whether or not dictionary keys will be yielded by ``pick``.

.. code-block:: python

    from handpick import pick

    root = {'key': {'str': 'Py', 'n': 1}, '_key': {'_str': '_Py', '_n': 2}}

    data = pick(root, lambda s: s.startswith('_'))
    data_with_keys = pick(root, lambda s: s.startswith('_'), dict_keys=True)

.. code::

    >>> list(data)
    ['_Py']
    >>> list(data_with_keys)
    ['_key', '_str', '_Py', '_n']


The ``predicate`` decorator and combining predicates
----------------------------------------------------

The ``predicate`` decorator returns objects that can be combined with other
predicates using the operators ``&`` (and) and ``|`` (or), as well as negated
using the operator ``~`` (not).

.. code-block:: python

    from handpick import pick, predicate

    @predicate
    def is_int(n):
        return isinstance(n, int)

    @predicate
    def is_even(n):
        return n % 2 == 0

    root = [[4, [5.0, 1], 3.0], [[15, []], {17: 7}], 9, [[8], 0, {13, ''}], 97]

    non_even_int = is_int & ~is_even
    odd_integers = pick(root, non_even_int)

.. code::

    >>> list(odd_integers)
    [1, 15, 7, 9, 13, 97]

Additionally, the ``&`` and ``|`` operations are supported between predicates
and regular functions.

.. code-block:: python

    from handpick import pick, predicate

    @predicate
    def is_list(obj):
        return isinstance(obj, list)

    root = [('1', [2]), {('x',): [(3, [4]), '5']}, ['x', [['6']]], {7: ('x',)}]

    short_list = (lambda obj: len(obj) < 2) & is_list
    short_lists = pick(root, short_list)

.. code::

    >>> list(short_lists)
    [[2], [4], [['6']], ['6']]


Built-in predicates
-------------------

.. code-block:: python

    from handpick import pick, NO_CONTAINERS

    data = [[], [0], [[[], 1], [2, [3, [4]], []], [5]]]
    flat_data = pick(data, NO_CONTAINERS)

.. code::

    >>> list(flat_data)
    [0, 1, 2, 3, 4, 5]


The ``flat`` shortcut function
------------------------------

To flatten a nested data structure as in the previous example,
the ``flat`` shortcut function can be used.

.. code-block:: python

    from handpick import flat

    data = [[], [0], [[[], 1], [2, [3, [4]], []], [5]]]
    flat_data = flat(data)

.. code::

    >>> list(flat_data)
    [0, 1, 2, 3, 4, 5]


Predicate factories
-------------------

The ``is_type`` and ``not_type`` functions can be used to create predicates
based on an object's type.

.. code-block:: python

    from handpick import pick, is_type, not_type

    root = [[1.0, [2, True], False], [False, [3]], [[4.5], '6', {7, True}]]
    integers_only = pick(root, is_type(int) & not_type(bool))

.. code::

    >>> list(integers_only)
    [2, 3, 7]


The ``max_depth`` function
--------------------------

.. code-block:: python

    from handpick import max_depth

    nested_list = [0, [1, [2]]]
    nested_dict = {0: {1: {2: {3: [4]}}}}

.. code::

    >>> max_depth(nested_list)
    2
    >>> max_depth(nested_dict)
    4

API reference
-------------

handpick.pick(root, predicate, dict_keys=False, strings=False, bytes_like=False)
    Pick objects from ``root`` based on ``predicate``.

    Traverse ``root`` recursively and yield all objects for which
    ``predicate(obj)`` is true.

    ``root`` should be an iterable container.

    ``predicate`` should be a callable taking one argument and returning
    a Boolean value. If ``predicate`` is not callable, equality will be
    used as the picking criteria, i.e. objects for which
    ``obj == predicate`` is true will be yielded.

    When traversing a mapping, only its values are inspected by
    default. If ``dict_keys`` is set to True, both keys and values of the
    mapping are inspected.

    By default, strings are not considered containers and thus not
    visited by the recursive algorithm. This can be changed by setting
    ``strings`` to True. Strings of length 0 or 1 are never visited.

    By default, bytes-like sequences (bytes and bytearrays) are not
    considered containers and thus not visited by the recursive
    algorithm. This can be changed by setting ``bytes_like`` to True.

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

    When traversing a mapping, only its values are considered.

handpick.max_depth(root)
    Return maximum nested depth of ``root``.

    ``root`` should be an iterable container. Direct elements of ``root``
    are considered to be in depth 0. Empty containers do not constitute
    another level of nested depth.


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
