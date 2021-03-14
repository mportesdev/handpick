from functools import reduce
import itertools
import operator

import pytest

from handpick import pick

FLAT = (6268, 0, True, 'food', '', None, [], 'foo')
STRINGS = ['foot', ['', 'foobar'], {'foo': 'bar', 'bar': 'fool'}, 'good food']
NUM_STRINGS = ['1', [' +2', '+1 '], {'-1': '.2', ' 1 ': '1.'}, '', ' - 0.3 ']
DICT = {1: [{}, 2], 2: [{}, [2, {}]]}
NESTED_LIST = [[1, 2, 100.0], [3, 'Py', [{}, 4], 5]]


def is_int(obj):
    return isinstance(obj, int)


params = (
    pytest.param(FLAT,
                 bool,
                 ([0], [2], [3], [7]),
                 id='flat - bool'),

    # isinstance
    pytest.param(FLAT,
                 is_int,
                 ([0], [1], [2]),
                 id='flat - is int'),
    pytest.param(FLAT,
                 lambda obj: isinstance(obj, str),
                 ([3], [4], [7]),
                 id='flat - is str'),
    pytest.param(STRINGS,
                 lambda obj: isinstance(obj, str),
                 ([0], [1, 0], [1, 1], [2, 'foo'], [2, 'bar'], [3]),
                 id='strings - is str'),
    pytest.param(NESTED_LIST,
                 is_int,
                 ([0, 0], [0, 1], [1, 0], [1, 2, 1], [1, 3]),
                 id='nested list - is int'),
    pytest.param(NESTED_LIST,
                 lambda obj: isinstance(obj, list),
                 ([0], [1], [1, 2]),
                 id='nested list - is list'),

    # int, float (can raise ValueError, TypeError)
    pytest.param(NUM_STRINGS,
                 lambda obj: int(obj) == 1,
                 ([0], [1, 1]),
                 id='num strings - int 1'),
    pytest.param(NUM_STRINGS,
                 lambda obj: float(obj) == 1,
                 ([0], [1, 1], [2, ' 1 ']),
                 id='num strings - float 1'),

    # index (can raise IndexError, KeyError)
    pytest.param(NESTED_LIST,
                 lambda obj: obj[2] is not None,
                 ([0], [1]),
                 id='nested list - item 2'),

    # len (can raise AttributeError)
    pytest.param(FLAT,
                 lambda obj: len(obj) == 0,
                 ([4], [6]),
                 id='flat - len 0'),

    # contains (can raise TypeError)
    pytest.param(FLAT,
                 lambda obj: 'foo' in obj,
                 ([3], [7]),
                 id='flat - contains "foo"'),
    pytest.param(STRINGS,
                 lambda obj: 'foo' in obj,
                 ([0], [1, 1], [2], [2, 'bar'], [3]),
                 id='strings - contains "foo"'),

    # hasattr
    pytest.param(FLAT,
                 lambda obj: hasattr(obj, '__iter__'),
                 ([3], [4], [6], [7]),
                 id='flat - has __iter__'),
)


def retrieve_items(obj, getitem_paths):
    yield from (
        reduce(operator.getitem, [obj, *getitem_path])
        for getitem_path in getitem_paths
    )


@pytest.mark.parametrize('data, predicate, routes_to_expected', params)
def test_pick(data, predicate, routes_to_expected):
    result = pick(data, predicate)
    expected_items = retrieve_items(data, routes_to_expected)

    # Unique object to make the assertion fail if `actual` and
    # `expected` are of unequal length
    sentinel = object()

    for actual, expected in itertools.zip_longest(result, expected_items,
                                                  fillvalue=sentinel):
        assert actual is expected


@pytest.mark.parametrize(
    'data, predicate, expected',
    (
        pytest.param(STRINGS,
                     lambda obj: isinstance(obj, str),
                     ['foot', '', 'foobar', 'foo', 'bar', 'bar', 'fool',
                      'good food'],
                     id='strings - is str'),
        pytest.param(STRINGS,
                     lambda obj: 'foo' in obj,
                     ['foot', 'foobar', {'foo': 'bar', 'bar': 'fool'},
                      'foo', 'fool', 'good food'],
                     id='strings - contains "foo"'),
        pytest.param(DICT, 1, [1], id='simple dict 1'),
        pytest.param(DICT, 2, [2, 2, 2], id='simple dict 2'),
        pytest.param(DICT, lambda n: 1 <= n <= 2, [1, 2, 2, 2],
                     id='simple dict 1-2'),
    )
)
def test_pick_including_dict_keys(data, predicate, expected):
    assert list(pick(data, predicate, dict_keys=True)) == expected
