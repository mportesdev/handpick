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
