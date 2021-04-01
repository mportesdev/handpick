|pytest| |release| |license| |pyversions| |format| |downloads|

Handpick is a tool to traverse nested data structures recursively and
find all objects that meet certain criteria.

Example 1: simple predicate functions
-------------------------------------

.. code-block:: python

    from handpick import pick

    data = [[1, 2, 100.0], [3, 'Py', [{}, 4], 5]]

    print(list(pick(data, lambda n: n > 3)))
    print(list(pick(data, lambda n: n > 3 and isinstance(n, int))))
    print(list(pick(data, lambda seq: len(seq) == 2)))

.. code::

    [100.0, 4, 5]
    [4, 5]
    ['Py', [{}, 4]]

Example 2: non-callable predicate
---------------------------------

This can be used e.g. to count occurrences of a value regardless of
the nested depth.

.. code-block:: python

    from handpick import pick

    data = [1, [1., [2, 1]], [{'id': 1, 'data': [0, 1.0]}, 1, [{}, [1]], 0]]

    ones = pick(data, 1)

.. code::

    >>> len(list(ones))
    7

Example 3: handling dictionary keys
-----------------------------------

.. code-block:: python

    from handpick import pick

    data = {'key': {'str': 'Py', 'n': 1}, '_key': {'_str': '_Py', '_n': 2}}

    no_keys = pick(data, lambda s: s.startswith('_'))
    with_keys = pick(data, lambda s: s.startswith('_'), dict_keys=True)

.. code::

    >>> list(no_keys)
    ['_Py']
    >>> list(with_keys)
    ['_key', '_str', '_Py', '_n']

Example 4: compound predicate
-----------------------------

.. code-block:: python

    from handpick import pick, predicate

    @predicate
    def is_int(n):
        return isinstance(n, int)

    @predicate
    def is_even(n):
        return n % 2 == 0

    data = [[4, [5.0, 1], 3.0], [[15, []], {17: 7}], 9, [[8], 0, {13, ''}], 97]

    non_even_int = is_int & ~is_even
    odd_integers = pick(data, non_even_int)

.. code::

    >>> list(odd_integers)
    [1, 15, 7, 9, 13, 97]


Example 5: predefined predicate
-------------------------------

.. code-block:: python

    from handpick import pick, NO_CONTAINERS

    root = {1: [{}, (2, '3')], 4: [{}, [5, ()]]}

    data = pick(root, NO_CONTAINERS)

.. code::

    >>> list(data)
    [2, '3', 5]


API reference
-------------

handpick.pick(root, predicate, dict_keys=False, strings=False, bytes_like=False)
    Yield all objects recursively from ``root`` for which
    ``predicate(obj)`` is true.

    ``root`` should be an iterable container. ``predicate`` should be a
    callable taking one object as argument and returning a Boolean
    value. If ``predicate`` is not callable, equality will be used as the
    picking criteria, i.e. objects for which ``obj == predicate`` is true
    will be yielded.

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
    the operators ``&`` (and), ``|`` (or) and ``~`` (not). The resulting
    object can be passed as the ``predicate`` argument to ``pick``.

handpick.NO_CONTAINERS
    Predicate that returns False for all iterable objects except
    strings and bytes-like objects.

handpick.NO_LIST_DICT
    Predicate that returns False for instances of ``list`` and
    ``dict``.


.. |pytest| image:: https://github.com/mportesdev/handpick/workflows/pytest/badge.svg
    :target: https://github.com/mportesdev/handpick/actions
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
