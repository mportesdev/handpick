Handpick
========

Handpick is a tool to inspect nested data structures recursively and find all objects that meet certain criteria.

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

This can be used e.g. to count occurrences of a value regardless of nested depth.

.. code-block:: python

    from handpick import pick

    data = [1, [1., [2, 1]], [{'id': 1, 'data': [0, 1.0]}, 1, [{}, [1]], 0]]

    print(len(list(pick(data, 1))))

.. code::

    7

Example 3: handling dictionary keys
-----------------------------------

.. code-block:: python

    from handpick import pick

    data = {'key': {'str': 'Py', 'n': 1}, '_key': {'_str': '_Py', '_n': 2}}

    print(list(pick(data, lambda s: s.startswith('_'))))
    print(list(pick(data, lambda s: s.startswith('_'), dict_keys=True)))

.. code::

    ['_Py']
    ['_key', '_str', '_Py', '_n']

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

    By default, strings are not considered containers and therefore not
    visited by the recursive algorithm. This can be changed by setting
    ``strings`` to True. Strings of length 0 or 1 are never visited.

    By default, bytes-like sequences (bytes and bytearrays) are not
    considered containers and therefore not visited by the recursive
    algorithm. This can be changed by setting ``bytes_like`` to True.
