from functools import reduce
import itertools
import json
import operator
from pathlib import Path

import pytest

from handpick import pick, predicate

TEST_DATA_PATH = Path(__file__).parent / 'data'

FLAT = (6268, 0, True, 'food', '', None, [], 'foo')
STRINGS = ['foot', ['', 'foobar'], {'foo': 'bar', 'bar': 'fool'}, 'good food']
NUM_STRINGS = ['1', [' +2', '+1 '], {'-1': '.2', ' 1 ': '1.'}, '', ' - 0.3 ']
DICT = {1: [{}, 2], 2: [{}, [2, {}]]}
NESTED_LIST = [[1, 2, 100.0], [3, 'Py', [{}, 4], 5]]
ONES = [1, [1., [2, 1]], [{'id': 1, 'data': [0, 1.0]}, 1, [{}, [1]], 0]]
NESTED_DICT_1 = {'key': {'str': 'Py', 'n': 1}, '_key': {'_str': '_Py', '_n': 2}}

NESTED_DICT_2 = {
    '1': {
        'dict': {
            'list': [],
            'tuple': (),
        },
        'list': [1, [2, [3, {}]]],
    },
    '2': {
        'dict': {
            'list': [],
            'tuple': (),
        },
        'tuple': ({}, [], ()),
    },
}


def is_int(obj):
    return isinstance(obj, int)


def is_str(obj):
    return isinstance(obj, str)


def from_json(filename):
    with open(TEST_DATA_PATH / filename) as f:
        data = json.load(f)
    return data


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
                 is_str,
                 ([3], [4], [7]),
                 id='flat - is str'),
    pytest.param(STRINGS,
                 is_str,
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
    pytest.param(NESTED_DICT_2,
                 lambda obj: isinstance(obj, dict),
                 (['1'], ['1', 'dict'], ['1', 'list', 1, 1, 1], ['2'],
                  ['2', 'dict'], ['2', 'tuple', 0]),
                 id='nested dict 2 - is dict'),
    pytest.param(NESTED_DICT_2,
                 lambda obj: isinstance(obj, list),
                 (['1', 'dict', 'list'], ['1', 'list'], ['1', 'list', 1],
                  ['1', 'list', 1, 1], ['2', 'dict', 'list'],
                  ['2', 'tuple', 1]),
                 id='nested dict 2 - is list'),
    pytest.param(NESTED_DICT_2,
                 is_str,
                 # only keys are strings
                 [],
                 id='nested dict 2 - is str'),

    # int, float (can raise ValueError, TypeError)
    pytest.param(NUM_STRINGS,
                 lambda obj: int(obj) == 1,
                 ([0], [1, 1]),
                 id='num strings - int 1'),
    pytest.param(NUM_STRINGS,
                 lambda obj: float(obj) == 1,
                 ([0], [1, 1], [2, ' 1 ']),
                 id='num strings - float 1'),

    # subscript (can raise IndexError, KeyError)
    pytest.param(NESTED_LIST,
                 lambda obj: obj[2] is not None,
                 ([0], [1]),
                 id='nested list - item 2'),

    # len (can raise TypeError)
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
    pytest.param(NESTED_DICT_2,
                 lambda obj: hasattr(obj, 'items'),
                 (['1'], ['1', 'dict'], ['1', 'list', 1, 1, 1], ['2'],
                  ['2', 'dict'], ['2', 'tuple', 0]),
                 id='nested dict 2 - has items'),

    # composite predicate
    pytest.param(NESTED_DICT_2,
                 lambda obj: isinstance(obj, dict) and obj,
                 (['1'], ['1', 'dict'], ['2'], ['2', 'dict']),
                 id='nested dict 2 - non-empty dict'),
)


@pytest.mark.parametrize(
    'data, predicate, expected',
    (
        pytest.param(NESTED_LIST, lambda n: n > 3, [100.0, 4, 5],
                     id='greater than 3'),
        pytest.param(NESTED_LIST, lambda n: n > 3 and isinstance(n, int),
                     [4, 5], id='int greater than 3'),
        pytest.param(NESTED_LIST, lambda seq: len(seq) == 2, ['Py', [{}, 4]],
                     id='len 2'),
        pytest.param(ONES, 1, [1] * 7, id='ones'),
    )
)
def test_simple_case(data, predicate, expected):
    """Test examples from README."""
    assert list(pick(data, predicate)) == expected


@pytest.mark.parametrize(
    'dict_keys, expected',
    (
        pytest.param(False, ['_Py'], id='without keys'),
        pytest.param(True, ['_key', '_str', '_Py', '_n'], id='with keys'),
    )
)
def test_simple_case_dict_keys(dict_keys, expected):
    """Test examples from README."""
    result = list(pick(NESTED_DICT_1, lambda s: s.startswith('_'), dict_keys))
    assert result == expected


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
        pytest.param(NESTED_DICT_2,
                     is_str,
                     ['1', 'dict', 'list', 'tuple', 'list', '2', 'dict', 'list',
                      'tuple', 'tuple'],
                     id='nested dict 2 - is str'),
        pytest.param(STRINGS,
                     is_str,
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


@pytest.mark.parametrize(
    'root',
    (
        pytest.param([], id='list'),
        pytest.param((), id='tuple'),
        pytest.param({}, id='dict'),
    )
)
def test_empty_root_yields_nothing(root):
    assert list(pick(root, lambda x: True)) == []


@pytest.mark.parametrize(
    'root',
    (
        pytest.param(0, id='int'),
        pytest.param(1.0, id='float'),
        pytest.param(True, id='bool'),
        pytest.param(None, id='None'),
        pytest.param(hash, id='builtin'),
    )
)
def test_non_iterable_root_yields_nothing(root):
    assert list(pick(root, lambda x: True)) == []


NESTED_DATA = {
    1: (
        {
            'f': (2.8419, 0.0923, 645.0, 1),
            'r': (2.8551, 0.0910, 1),
            'l': (2.8488, 0.0914, 1),
            'p': (2.8419, 0.0923, 645.0, 1.0),
        },
        [None, [[0., 1., 0., None], None]],
    ),
    2: (
        {
            'f': (2.7806, 0.0627, 642.0, 2),
            'r': (5.6047, 0.0606, 2),
            'l': (5.5805, 0.0614, 2),
            'p': (2.7806, 0.0627, 642.0, 2.0),
        },
        [None, [[0., 0., 1., 0., 0.], None, [0., 0., None, 0., 1., 0.]]],
    ),
    3: (
        {
            'f': (2.1251, 0.0958, 639.0, 3),
            'r': (6.4452, 0.0918, 3),
            'l': (6.4132, 0.0931, 3),
            'p': (2.1251, 0.0958, 639.0, 3.0),
        },
        [None, [[0., 1., 0.], None, [0., 1., 0.], [0., None, [0., None], 1.]]],
    ),
}


@pytest.mark.parametrize(
    'root, predicate, expected_len',
    (
        pytest.param([1, 2, 3], 1, 1, id='1'),
        pytest.param([1, 2, 3], None, 0, id='None'),
        pytest.param([[1, 2], [2, 3]], 2, 2, id='2'),
        pytest.param(DICT, 1, 0, id='simple dict 1'),
        pytest.param(DICT, 2, 2, id='simple dict 2'),
        pytest.param(DICT, {}, 3, id='simple dict {}'),
        pytest.param(ONES, 1.0, 7, id='ones'),
        pytest.param(NESTED_DATA, 0.0606, 1, id='float'),
        pytest.param(NESTED_DATA, 1, 10, id='float'),
        pytest.param(NESTED_DATA, None, 10, id='float'),
    )
)
def test_non_callable_predicate(root, predicate, expected_len):
    assert list(pick(root, predicate)) == [predicate] * expected_len


@pytest.mark.parametrize(
    'root, expected',
    (
            pytest.param(['str'], ['str'], id='flat'),
            pytest.param((['ab'], 'cd'), ['ab', 'cd'], id='nested'),
            pytest.param({'ef': 'gh'}, ['ef', 'gh'], id='dict'),
            pytest.param('str', [], id='str'),
    )
)
def test_strings_not_iterated_by_default(root, expected):
    assert list(pick(root, is_str,
                     dict_keys=True)) == expected


@pytest.mark.parametrize(
    'root, expected',
    (
            pytest.param(['str'], ['str', 's', 't', 'r'], id='flat'),
            pytest.param((['ab'], 'cd'), ['ab', 'a', 'b', 'cd', 'c', 'd'],
                         id='nested'),
            pytest.param({'ef': 'gh'}, ['ef', 'e', 'f', 'gh', 'g', 'h'],
                         id='dict'),
            pytest.param('str', ['s', 't', 'r'], id='str'),
    )
)
def test_strings_iterated_optionally(root, expected):
    assert list(pick(root, is_str,
                     dict_keys=True, strings=True)) == expected


@pytest.mark.parametrize(
    'root, expected',
    (
            pytest.param(b'01', [], id='bytes'),
            pytest.param([b'AB'], [], id='flat'),
            pytest.param((0, [[bytearray([1, 2])], b'12'], 1), [0, 1],
                         id='nested'),
            pytest.param({bytes([1, 2]): bytearray(b'\003\004')}, [],
                         id='dict'),
            pytest.param(bytearray(b'ab'), [], id='bytearray'),
    )
)
def test_bytes_like_not_iterated_by_default(root, expected):
    result = list(pick(root, is_int, dict_keys=True))
    assert result == expected


@pytest.mark.parametrize(
    'root, expected',
    (
            pytest.param(b'01', [48, 49], id='bytes'),
            pytest.param([b'AB'], [65, 66], id='flat'),
            pytest.param((0, [[bytearray([1, 2])], b'12'], 1),
                         [0, 1, 2, 49, 50, 1], id='nested'),
            pytest.param({bytes([1, 2]): bytearray(b'\003\004')}, [1, 2, 3, 4],
                         id='dict'),
            pytest.param(bytearray(b'ab'), [97, 98], id='bytearray'),
    )
)
def test_bytes_like_iterated_optionally(root, expected):
    result = list(pick(root, is_int, dict_keys=True, bytes_like=True))
    assert result == expected


def test_predicate_and_predicate():
    """Test the overloaded `&` operation between two Predicates."""

    @predicate
    def is_str(s):
        return isinstance(s, str)

    @predicate
    def is_short(s):
        return len(s) < 3

    short_string = is_str & is_short

    data = [('1', [0, 1]), {'long': {(2,), '2'}}, range(2), 'long', {3: 'long'}]
    result = list(pick(data, short_string))
    assert result == ['1', '2']


def test_predicate_and_non_predicate_not_implemented():
    """Test the overloaded `&` operation between a predicate and
    a regular function.
    """
    @predicate
    def is_str(s):
        return isinstance(s, str)

    with pytest.raises(TypeError, match='unsupported operand type'):
        pick([], is_str & len)


def test_predicate_or_predicate():
    """Test the overloaded `|` operation between two Predicates."""

    @predicate
    def is_int(n):
        return isinstance(n, int)

    @predicate
    def is_roundable(obj):
        return hasattr(obj, '__round__')

    can_be_int = is_int | is_roundable

    data = [('1', [None, 9.51]), {'': {2., '2'}}, range(5, 7), '2', {3: True}]
    result = list(pick(data, can_be_int))
    assert result == [9.51, 2., 5, 6, True]


def test_predicate_or_non_predicate_not_implemented():
    """Test the overloaded `|` operation between a predicate and
    a regular function.
    """
    @predicate
    def is_str(s):
        return isinstance(s, str)

    with pytest.raises(TypeError, match='unsupported operand type'):
        pick([], is_str | callable)


def test_not_predicate():
    """Test the overloaded `~` operation with a predicate."""

    @predicate
    def is_long(s):
        return len(s) > 2

    is_short = ~is_long

    data = [('1', [0, 1], None), {'long': '2'}, range(2), 'long', {3, False, 1}]
    result = list(pick(data, is_short))
    assert result == ['1', [0, 1], {'long': '2'}, '2', range(2)]


def test_compound_predicate():
    """Test a compound predicate using the overloaded operations
    `&`, `|` and `~`.
    """
    @predicate
    def is_int(n):
        return isinstance(n, int)

    @predicate
    def is_even(n):
        return n % 2 == 0

    falsey = ~predicate(bool)

    odd_or_zero_int = is_int & (~is_even | falsey)

    data = [[4, [5.0, 1], 3.0], [[15, []], {17: 7}], 9, [[8], 0, {13, ''}], 97]
    result = list(pick(data, odd_or_zero_int))
    assert result == [1, 15, 7, 9, 0, 13, 97]
