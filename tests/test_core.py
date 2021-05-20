import functools
import itertools
import json
import operator
from pathlib import Path

import pytest

from handpick import (
    pick,
    predicate,
    is_type,
    not_type,
    NO_CONTAINERS,
    values_for_key,
    max_depth,
)
from handpick.core import _iter_depth

TEST_DATA_PATH = Path(__file__).parent / 'data'

FLAT = (62, 0.0, True, 'food', '', None, [], 'foo', {})

NESTED_LIST = [
    [1, 2, 100.0],
    [3, 'Py', [{}, 4], 5],
]

DICT_LIST = {
    1: [
        {},
        (2, '3'),
    ],
    4: [
        {},
        [5, ()],
    ],
}

LIST_TUPLE = [
    [
        None,
        (
            (1, 2, 3),
            3,
        ),
        0,
    ],
    ('foo', 'bar'),
]

NESTED_DICT = {
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

LIST_5_LEVELS = [
    [
        [
            bytearray(b'2'),
            [
                ['4'],
                3.5,
            ],
        ],
        b'1',
    ],
    '0',
    [
        [
            '2',
            [b'3'],
        ],
        '1',
        (2,),
    ],
]

DICT_5_LEVELS = {
    '0_key1': '0_value1',
    '0_key2': {
        '1_key1': {
            '2_key1': '2_value1',
            '2_key2': {
                '3_key1': {'4_key': '4_value'},
                '3_key2': {'4_value2'}
            },
        },
        '1_key2': '1_value2',
    },
}


def is_int(obj):
    return isinstance(obj, int)


def is_str(obj):
    return isinstance(obj, str)


def is_list(obj):
    return isinstance(obj, list)


def is_tuple(obj):
    return isinstance(obj, tuple)


def from_json(filename):
    with open(TEST_DATA_PATH / filename) as f:
        data = json.load(f)
    return data


def retrieve_items(obj, routes):
    yield from (
        functools.reduce(operator.getitem, [obj, *route])
        for route in routes
    )


class TestPick:

    @pytest.mark.parametrize(
        'root, predicate, expected',
        (
            pytest.param(FLAT, bool, [62, True, 'food', 'foo'],
                         id='flat - bool'),
            pytest.param(NESTED_LIST, bool,
                         [[1, 2, 100.0], 1, 2, 100.0, [3, 'Py', [{}, 4], 5],
                          3, 'Py', [{}, 4], 4, 5],
                         id='nested dict - is list'),
        )
    )
    def test_bool(self, root, predicate, expected):
        assert list(pick(root, predicate)) == expected

    @pytest.mark.parametrize(
        'root, predicate, expected',
        (
            pytest.param(FLAT, is_str, ['food', '', 'foo'],
                         id='flat - is str'),
            pytest.param(LIST_TUPLE, is_tuple,
                         [((1, 2, 3), 3), (1, 2, 3), ('foo', 'bar')],
                         id='list tuple - is tuple'),
            pytest.param(NESTED_LIST, is_int, [1, 2, 3, 4, 5],
                         id='nested list - is int'),
        )
    )
    def test_isinstance(self, root, predicate, expected):
        assert list(pick(root, predicate)) == expected

    @pytest.mark.parametrize(
        'root, predicate, expected',
        (
            pytest.param(FLAT, lambda obj: float(obj) < 50, [0.0, True],
                         id='flat - float < 50'),
            pytest.param(LIST_5_LEVELS, lambda obj: int(obj) >= 0,
                         [bytearray(b'2'), '4', 3.5, b'1', '0', '2', b'3',
                          '1', 2],
                         id='list 5 levels - int >= 0'),
        )
    )
    def test_int_float(self, root, predicate, expected):
        assert list(pick(root, predicate)) == expected

    @pytest.mark.parametrize(
        'root, predicate, expected',
        (
            pytest.param(FLAT, lambda obj: obj[2], ['food', 'foo'],
                         id='flat - item 2'),
            pytest.param(NESTED_LIST, lambda obj: obj[1],
                         [[1, 2, 100.0], [3, 'Py', [{}, 4], 5], 'Py',
                          [{}, 4]],
                         id='nested list - item 3'),
        )
    )
    def test_subscript(self, root, predicate, expected):
        assert list(pick(root, predicate)) == expected

    @pytest.mark.parametrize(
        'root, predicate, expected',
        (
            pytest.param(FLAT, lambda obj: len(obj) == 0, ['', [], {}],
                         id='flat - len 0'),
            pytest.param(LIST_TUPLE, lambda obj: len(obj) == 3,
                         [[None, ((1, 2, 3), 3), 0], (1, 2, 3), 'foo',
                          'bar'],
                         id='list tuple - len 3'),
        )
    )
    def test_len(self, root, predicate, expected):
        assert list(pick(root, predicate)) == expected

    @pytest.mark.parametrize(
        'root, predicate, expected',
        (
            pytest.param(FLAT, lambda obj: 'foo' in obj, ['food', 'foo'],
                         id='flat - contains "foo"'),
            pytest.param(LIST_TUPLE, lambda obj: 3 in obj,
                         [((1, 2, 3), 3), (1, 2, 3)],
                         id='list tuple - contains 3'),
        )
    )
    def test_contains(self, root, predicate, expected):
        assert list(pick(root, predicate)) == expected

    @pytest.mark.parametrize(
        'root, predicate, expected',
        (
            pytest.param(FLAT, lambda obj: hasattr(obj, 'count'),
                         ['food', '', [], 'foo'],
                         id='flat - has .count'),
            pytest.param(NESTED_DICT, lambda obj: hasattr(obj, 'append'),
                         [[], [1, [2, [3, {}]]], [2, [3, {}]], [3, {}], [], []],
                         id='nested dict - has .append'),
        )
    )
    def test_hasattr(self, root, predicate, expected):
        assert list(pick(root, predicate)) == expected

    @pytest.mark.parametrize(
        'root, predicate, expected',
        (
            pytest.param(FLAT, lambda obj: isinstance(obj, float) and obj % 2,
                         [],
                         id='flat - odd float'),
            pytest.param(NESTED_DICT,
                         lambda obj: isinstance(obj, dict) and not obj,
                         [{}, {}],
                         id='nested dict - empty dict'),
        )
    )
    def test_composite(self, root, predicate, expected):
        assert list(pick(root, predicate)) == expected

    @pytest.mark.parametrize(
        'root, predicate, routes',
        (
            pytest.param(FLAT, lambda obj: float(obj) < 50, [[1], [2]],
                         id='flat - float < 50'),
            pytest.param(NESTED_LIST, lambda obj: obj[1],
                         [[0], [1], [1, 1], [1, 2]],
                         id='nested list - item 3'),
            pytest.param(LIST_TUPLE, lambda obj: 3 in obj, [[0, 1], [0, 1, 0]],
                         id='list tuple - contains 3'),
            pytest.param(NESTED_DICT,
                         lambda obj: isinstance(obj, dict) and not obj,
                         [['1', 'list', 1, 1, 1], ['2', 'tuple', 0]],
                         id='nested dict - empty dict'),
        )
    )
    def test_picked_objects_by_identity(self, root, predicate, routes):
        result = pick(root, predicate)
        expected_items = retrieve_items(root, routes)

        # Unique object to make the assertion fail if `actual` and
        # `expected` are of unequal length
        sentinel = object()

        for actual, expected in itertools.zip_longest(result, expected_items,
                                                      fillvalue=sentinel):
            assert actual is expected


class TestPickDictKeysHandling:

    STRINGS = ['foot', ['', 'foobar'], {'foo': 'bar', 'bar': 'fool'},
               'good food']

    @pytest.mark.parametrize(
        'root, predicate, expected',
        (
            pytest.param(STRINGS, is_str,
                         ['foot', '', 'foobar', 'bar', 'fool', 'good food'],
                         id='strings - is str'),
            pytest.param(STRINGS, lambda obj: 'foo' in obj,
                         ['foot', 'foobar', {'foo': 'bar', 'bar': 'fool'},
                          'fool', 'good food'],
                         id='strings - contains "foo"'),
            pytest.param(DICT_LIST, lambda n: 2 <= n <= 4, [2],
                         id='dict list - 2-4'),
            pytest.param(NESTED_DICT, is_str, [], id='nested dict - is str'),
        )
    )
    def test_pick_no_keys(self, root, predicate, expected):
        assert list(pick(root, predicate)) == expected

    @pytest.mark.parametrize(
        'root, predicate, expected',
        (
            pytest.param(STRINGS, is_str,
                         ['foot', '', 'foobar', 'foo', 'bar', 'bar', 'fool',
                          'good food'],
                         id='strings - is str'),
            pytest.param(STRINGS, lambda obj: 'foo' in obj,
                         ['foot', 'foobar', {'foo': 'bar', 'bar': 'fool'},
                          'foo', 'fool', 'good food'],
                         id='strings - contains "foo"'),
            pytest.param(DICT_LIST, lambda n: 2 <= n <= 4, [2, 4],
                         id='dict list - 2-4'),
            pytest.param(NESTED_DICT, is_str,
                         ['1', 'dict', 'list', 'tuple', 'list', '2', 'dict',
                          'list', 'tuple', 'tuple'],
                         id='nested dict - is str'),
        )
    )
    def test_pick_including_keys(self, root, predicate, expected):
        assert list(pick(root, predicate, dict_keys=True)) == expected


class TestPickSpecialCases:

    @pytest.mark.parametrize('predicate', (lambda x: True, bool, abs))
    @pytest.mark.parametrize(
        'root',
        (
            pytest.param([], id='list'),
            pytest.param((), id='tuple'),
            pytest.param({}, id='dict'),
        )
    )
    def test_empty_root_yields_nothing(self, root, predicate):
        assert list(pick(root, predicate)) == []

    @pytest.mark.parametrize('predicate', (lambda x: True, bool, abs))
    @pytest.mark.parametrize(
        'root',
        (
            pytest.param(0, id='int'),
            pytest.param(None, id='None'),
            pytest.param(hash, id='builtin'),
        )
    )
    def test_non_iterable_root_yields_nothing(self, root, predicate):
        assert list(pick(root, predicate)) == []

    @pytest.mark.parametrize(
        'root, predicate, expected_len',
        (
            pytest.param([1, 2, 3], 1, 1, id='1'),
            pytest.param([1, 2, 3], None, 0, id='None'),
            pytest.param([[1, 2], [2, 3]], 2, 2, id='2'),
            pytest.param(DICT_LIST, {}, 2, id='dict list - {}'),
        )
    )
    def test_non_callable_predicate(self, root, predicate, expected_len):
        assert list(pick(root, predicate)) == [predicate] * expected_len


class TestPickStringsAndBytesLike:

    @pytest.mark.parametrize(
        'root, expected',
        (
            pytest.param([''], [''], id='flat list, empty string'),
            pytest.param(['a'], ['a'], id='flat list, single char string'),
            pytest.param(['str'], ['str'], id='flat list'),
            pytest.param((['ab'], 'cd'), ['ab', 'cd'], id='nested'),
            pytest.param({'ef': 'gh'}, ['gh'], id='dict'),
            pytest.param('', [], id='top-level string empty'),
            pytest.param('a', [], id='top-level string single char'),
            pytest.param('str', [], id='top-level string'),
        )
    )
    def test_strings_not_iterated_by_default(self, root, expected):
        assert list(pick(root, is_str)) == expected

    @pytest.mark.parametrize(
        'root, expected',
        (
            pytest.param([''], [''], id='flat list, empty string'),
            pytest.param(['a'], ['a'], id='flat list, single char string'),
            pytest.param(['str'], ['str', 's', 't', 'r'], id='flat list'),
            pytest.param((['ab'], 'cd'), ['ab', 'a', 'b', 'cd', 'c', 'd'],
                         id='nested'),
            pytest.param({'ef': 'gh'}, ['gh', 'g', 'h'], id='dict'),
            pytest.param('', [], id='top-level string empty'),
            pytest.param('a', [], id='top-level string single char'),
            pytest.param('str', ['s', 't', 'r'], id='top-level string'),
        )
    )
    def test_strings_iterated_optionally(self, root, expected):
        assert list(pick(root, is_str, strings=True)) == expected

    @pytest.mark.parametrize(
        'root, expected',
        (
            pytest.param([b''], [], id='flat list, empty bytes'),
            pytest.param([b'A'], [], id='flat list, bytes'),
            pytest.param((0, [[bytearray([1, 2])], b'12'], 1), [0, 1],
                         id='nested'),
            pytest.param({bytes([1, 2]): bytearray(b'\003\004')}, [],
                         id='dict'),
            pytest.param(b'', [], id='top-level bytes empty'),
            pytest.param(b'1', [], id='top-level bytes'),
            pytest.param(bytearray(b'ab'), [], id='top-level bytearray'),
        )
    )
    def test_bytes_like_not_iterated_by_default(self, root, expected):
        assert list(pick(root, is_int)) == expected

    @pytest.mark.parametrize(
        'root, expected',
        (
            pytest.param([b''], [], id='flat list, bytes empty'),
            pytest.param([b'A'], [65], id='flat list, bytes'),
            pytest.param((0, [[bytearray([1, 2])], b'12'], 1),
                         [0, 1, 2, 49, 50, 1], id='nested'),
            pytest.param({bytes([1, 2]): bytearray(b'\003\004')}, [3, 4],
                         id='dict'),
            pytest.param(b'', [], id='top-level bytes empty'),
            pytest.param(b'1', [49], id='top-level bytes'),
            pytest.param(bytearray(b'ab'), [97, 98], id='top-level bytearray'),
        )
    )
    def test_bytes_like_iterated_optionally(self, root, expected):
        assert list(pick(root, is_int, bytes_like=True)) == expected


class TestPredicates:

    def test_predicate_and_predicate(self):
        """Test the overloaded `&` operation between two predicates."""

        @predicate
        def is_str(obj):
            return isinstance(obj, str)

        @predicate
        def is_short(obj):
            return len(obj) < 3

        short_string = is_str & is_short

        root = [('1', [0, ['py']]), {'foo': {(2,), '2'}}, {b'A'}, 'foo',
                {3: 'foo'}]
        result = list(pick(root, short_string))
        assert result == ['1', 'py', '2']

    def test_predicate_and_function(self):
        """Test predicate & function."""

        @predicate
        def is_tuple(obj):
            return isinstance(obj, tuple)

        tuple_containing_2 = is_tuple & (lambda obj: 2 in obj)

        root = [('2', [2]), {'long': {(2,), '2'}}, range(2), 'long',
                {2: 'long'}]

        result = list(pick(root, tuple_containing_2))
        assert result == [(2,)]

    @pytest.mark.parametrize(
        'function, predicate, values, expected',
        (
            pytest.param(lambda obj: len(obj) < 2,
                         predicate(is_list),
                         [{}, [], '1', [2], {('foo',): []}, [{3}]],
                         [False, True, False, True, False, True]),
        )
    )
    def test_function_and_predicate(self, function, predicate, values,
                                    expected):
        """Test function & predicate."""
        compound_predicate = function & predicate

        for value, result in zip(values, expected):
            assert compound_predicate(value) is result

    def test_predicate_and_non_callable_raises_error(self):
        """Test predicate & non-callable."""

        @predicate
        def is_dunder_name(string):
            return string.startswith('__') and string.endswith('__')

        with pytest.raises(TypeError):
            is_dunder_name & True

    def test_predicate_or_predicate(self):
        """Test the overloaded `|` operation between two predicates."""

        @predicate
        def is_roundable(obj):
            return hasattr(obj, '__round__')

        can_be_int = predicate(is_int) | is_roundable

        root = [('1', [None, 9.51]), {'': {2., '2'}}, range(5, 7), '2',
                {3: True}]
        result = list(pick(root, can_be_int))
        assert result == [9.51, 2., 5, 6, True]

    def test_predicate_or_function(self):
        """Test predicate | function."""

        @predicate
        def is_tuple(obj):
            return isinstance(obj, tuple)

        tuple_or_contains_3 = is_tuple | (lambda obj: 3 in obj)

        root = [['1', 3], {'long': {(2,), '2'}}, range(4), 'long', {3: 'long'}]

        result = list(pick(root, tuple_or_contains_3))
        assert result == [['1', 3], (2,), range(4), {3: 'long'}]

    def test_function_or_predicate(self):
        """Test function | predicate."""

        @predicate
        def is_tuple(obj):
            return isinstance(obj, tuple)

        tuple_or_contains_3 = (lambda obj: 3 in obj) | is_tuple

        root = [['1', 3], {'long': {(2,), '2'}}, range(4), 'long', {3: 'long'}]

        result = list(pick(root, tuple_or_contains_3))
        assert result == [['1', 3], (2,), range(4), {3: 'long'}]

    def test_predicate_or_non_callable_raises_error(self):
        """Test predicate | non-callable."""

        @predicate
        def is_dunder_name(string):
            return string.startswith('__') and string.endswith('__')

        with pytest.raises(TypeError):
            is_dunder_name | True

    def test_not_predicate(self):
        """Test the overloaded `~` operation with a predicate."""

        @predicate
        def is_long(obj):
            return len(obj) > 2

        is_short = ~is_long

        root = [('1', [0, 1], None), {'long': '2'}, range(2), 'long',
                {3, False, 1}]
        result = list(pick(root, is_short))
        assert result == ['1', [0, 1], {'long': '2'}, '2', range(2)]

    def test_compound_predicate(self):
        """Test a compound predicate using the overloaded operations
        `&`, `|` and `~`.
        """
        @predicate
        def is_even(obj):
            return obj % 2 == 0

        falsey = ~predicate(bool)
        odd_or_zero_int = is_type(int) & (~is_even | falsey)

        root = [[4, [5.0, 11], 3], [[12, [0]], {17: 6}], 9, [[8], 0, {13, '1'}]]
        result = list(pick(root, odd_or_zero_int))
        assert result == [11, 3, 0, 9, 0, 13]

    def test_compound_predicate_with_functions(self):
        """Test a compound predicate combining predicates and functions."""

        @predicate
        def is_list_or_dict(obj):
            return isinstance(obj, (list, dict))

        @predicate
        def is_set(obj):
            return isinstance(obj, set)

        pred = (
            ~is_list_or_dict
            & ((bool & is_type(str)) | (~is_set & (lambda obj: len(obj) > 1)))
        )

        root = (['', 0, ['a']], {0: '', 1: (0, 'b')}, [{1, 2}, b'c'],
                {(), ('\\',)})
        result = list(pick(root, pred))
        assert result == ['a', (0, 'b'), 'b', '\\']


class TestBuiltinPredicates:

    @pytest.mark.parametrize(
        'root, expected',
        (
            pytest.param(LIST_5_LEVELS,
                         [bytearray(b'2'), '4', 3.5, b'1', '0', '2', b'3', '1',
                          2],
                         id='list 5 levels - no containers'),
            pytest.param(DICT_5_LEVELS,
                         ['0_value1', '2_value1', '4_value', '4_value2',
                          '1_value2'],
                         id='dict 5 levels - no containers'),
        )
    )
    def test_no_containers_predicate(self, root, expected):
        assert list(pick(root, NO_CONTAINERS)) == expected

    @pytest.mark.parametrize(
        'json_file',
        ('list_of_int.json', 'dict_of_int.json')
    )
    def test_no_containers_predicate_with_generated_data(self, json_file):
        root = from_json(json_file)
        for n in pick(root, NO_CONTAINERS):
            assert is_int(n)

    @pytest.mark.parametrize(
        'root, type_or_types, expected',
        (
            pytest.param(FLAT, str, ['food', '', 'foo'], id='flat - str'),
            pytest.param(FLAT, (list, dict), [[], {}], id='flat - list, dict'),
            pytest.param(NESTED_DICT, tuple, [(), (), ({}, [], ()), ()],
                         id='nested dict - tuple'),
            pytest.param(NESTED_DICT, (list, int),
                         [[], [1, [2, [3, {}]]], 1, [2, [3, {}]], 2, [3, {}], 3,
                          [], []],
                         id='nested dict - list, int'),
        )
    )
    def test_is_type_predicate(self, root, type_or_types, expected):
        assert list(pick(root, is_type(type_or_types))) == expected

    @pytest.mark.parametrize(
        'root, type_or_types, expected',
        (
            pytest.param(FLAT, str, [62, 0.0, True, None, [], {}],
                         id='flat - str'),
            pytest.param(FLAT, (list, dict),
                         [62, 0.0, True, 'food', '', None, 'foo'],
                         id='flat - list, dict'),
            pytest.param(LIST_TUPLE, list,
                         [None, ((1, 2, 3), 3), (1, 2, 3), 1, 2, 3, 3, 0,
                          ('foo', 'bar'), 'foo', 'bar'],
                         id='list tuple - list'),
            pytest.param(LIST_TUPLE, (str, tuple, list),
                         [None, 1, 2, 3, 3, 0],
                         id='list tuple - str, tuple'),
            pytest.param(NESTED_DICT, (dict, list),
                         [(), 1, 2, 3, (), ({}, [], ()), ()],
                         id='nested dict - dict, list'),
        )
    )
    def test_not_type_predicate(self, root, type_or_types, expected):
        assert list(pick(root, not_type(type_or_types))) == expected

    def test_combined_builtin_predicates(self):
        no_container_or_float = NO_CONTAINERS & not_type(float)
        no_binary = ~is_type((bytes, bytearray))

        root = LIST_5_LEVELS
        result = list(pick(root, no_container_or_float & no_binary))
        assert result == ['4', '0', '2', '1', 2]


class TestValuesForKey:

    @pytest.mark.parametrize(
        'data, key, expected',
        (
            pytest.param({}, 0, [], id='empty'),
            pytest.param({0: 1, 2: 3}, 0, [1], id='top-level key 0'),
            pytest.param({0: 1, 2: 3}, 1, [], id='top-level key missing'),
            pytest.param({0: 1, 2: 3}, 2, [3], id='top-level key 2'),
            pytest.param({0: {0: 1}}, 0, [{0: 1}, 1], id='same key, nested'),
            pytest.param({'a': {'b': 0}, 'b': 1}, 'b', [1, 0],
                         id='same key different level'),
            pytest.param([{'foo': [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}],
                           'bar': ({'x': 5}, {'x': 6})}], 'x', [1, 3, 5, 6],
                         id='list, dict, tuple x'),
            pytest.param([{'foo': [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}],
                           'bar': ({'x': 5}, {'x': 6})}], 'y', [2, 4],
                         id='list, dict, tuple y'),
        )
    )
    def test_values_for_key(self, data, key, expected):
        assert list(values_for_key(data, key)) == expected

    @pytest.mark.parametrize(
        'key, expected',
        (
            pytest.param('-98', [2532, 29553]),
            pytest.param('16399', [20528]),
        )
    )
    def test_values_for_key_with_generated_data(self, key, expected):
        data = from_json('dict_of_int.json')
        assert list(values_for_key(data, key)) == expected


class TestMaxDepthIterDepth:

    @pytest.mark.parametrize(
        'root, expected',
        (
            pytest.param(FLAT, 1, id='flat'),
            pytest.param(NESTED_LIST, 3, id='nested_list'),
            pytest.param(DICT_LIST, 3, id='dict_list'),
            pytest.param(LIST_TUPLE, 3, id='list_tuple'),
            pytest.param(NESTED_DICT, 5, id='nested_dict'),
            pytest.param(LIST_5_LEVELS, 4, id='list_5_levels'),
            pytest.param(DICT_5_LEVELS, 4, id='dict_5_levels'),
            pytest.param([], 0, id='[]'),
            pytest.param([[]], 1, id='[[]]'),
            pytest.param([[[]]], 2, id='[[[]]]'),
        )
    )
    def test_max_depth(self, root, expected):
        assert max_depth(root) == expected

    @pytest.mark.parametrize(
        'json_file, expected',
        (
            pytest.param('list_of_int.json', 12),
            pytest.param('dict_of_int.json', 5),
        )
    )
    def test_max_depth_with_generated_data(self, json_file, expected):
        root = from_json(json_file)
        assert max_depth(root) == expected

    @pytest.mark.parametrize(
        'root, expected',
        (
            pytest.param(FLAT, [0, 1, 1], id='flat'),
            pytest.param(NESTED_LIST, [0, 1, 1, 2, 3], id='nested_list'),
            pytest.param(DICT_LIST, [0, 1, 2, 2, 1, 2, 2, 3], id='dict_list'),
            pytest.param(LIST_TUPLE, [0, 1, 2, 3, 1], id='list_tuple'),
            pytest.param(NESTED_DICT,
                         [0, 1, 2, 3, 3, 2, 3, 4, 5, 1, 2, 3, 3, 2, 3, 3, 3],
                         id='nested_dict'),
            pytest.param(LIST_5_LEVELS, [0, 1, 2, 3, 4, 1, 2, 3, 2],
                         id='list_5_levels'),
            pytest.param(DICT_5_LEVELS, [0, 1, 2, 3, 4, 4], id='dict_5_levels'),
            pytest.param([], [0], id='[]'),
            pytest.param([[]], [0, 1], id='[[]]'),
            pytest.param([[[]]], [0, 1, 2], id='[[[]]]'),
        )
    )
    def test_iter_depth(self, root, expected):
        assert list(_iter_depth(root)) == expected


class TestFlattening:

    @pytest.mark.parametrize(
        'data, expected',
        (
            pytest.param(FLAT, [62, 0.0, True, 'food', '', None, 'foo'],
                         id='flat'),
            pytest.param(NESTED_LIST, [1, 2, 100.0, 3, 'Py', 4, 5],
                         id='nested list'),
            pytest.param(DICT_LIST, [2, '3', 5],
                         id='dict list'),
            pytest.param(LIST_TUPLE, [None, 1, 2, 3, 3, 0, 'foo', 'bar'],
                         id='list tuple'),
            pytest.param(NESTED_DICT, [1, 2, 3],
                         id='nested dict'),
            pytest.param(LIST_5_LEVELS, [bytearray(b'2'), '4', 3.5, b'1', '0',
                                         '2', b'3', '1', 2],
                         id='list 5 levels'),
            pytest.param(DICT_5_LEVELS, ['0_value1', '2_value1', '4_value',
                                         '4_value2', '1_value2'],
                         id='dict 5 levels'),
        )
    )
    def test_flattening(self, data, expected):
        assert list(pick(data, NO_CONTAINERS)) == expected


class TestReadmeExamples:
    """Test examples from README."""

    LIST = [[1, 'Py'], [-2, ['', 3.0]], -4]

    def test_example_1(self):
        """Example from 'Simple predicate functions'."""

        data = self.LIST
        non_empty_strings = pick(data, lambda s: isinstance(s, str) and s)

        assert list(non_empty_strings) == ['Py']

    def test_example_2(self):
        """Example from 'Non-callable predicates'."""

        data = [1, [1.0, [2, 1.]], [{'1': 1}, [3]]]
        ones = pick(data, 1)

        assert list(ones) == [1, 1.0, 1.0, 1]

    def test_example_3(self):
        """Example from 'Suppressing errors'."""

        def above_zero(n):
            return n > 0

        data = self.LIST
        positive_numbers = pick(data, above_zero)

        assert list(positive_numbers) == [1, 3.0]

    def test_example_4(self):
        """Example from 'Handling dictionary keys'."""

        data = {'key': {'name': 'foo'}, '_key': {'_name': '_bar'}}
        default = pick(data, lambda s: s.startswith('_'))
        keys_included = pick(data, lambda s: s.startswith('_'), dict_keys=True)

        assert list(default) == ['_bar']
        assert list(keys_included) == ['_key', '_name', '_bar']

    def test_example_5(self):
        """Example from 'Combining predicates'."""

        @predicate
        def is_int(n):
            return isinstance(n, int)

        @predicate
        def is_even(n):
            return n % 2 == 0

        data = [[4, [5.0, 1], 3.0], [[15, []], {17: [7, [8], 0]}]]
        non_even_int = is_int & ~is_even
        odd_integers = pick(data, non_even_int)

        assert list(odd_integers) == [1, 15, 7]

    def test_example_6(self):
        """Example from 'Combining predicates with functions'."""

        @predicate
        def is_list(obj):
            return isinstance(obj, list)

        data = [('1', [2]), {('x',): [(3, [4]), '5']}, ['x', ['6']], {7: ('x',)}]
        short_list = (lambda obj: len(obj) < 2) & is_list
        short_lists = pick(data, short_list)

        assert list(short_lists) == [[2], [4], ['6']]

    def test_example_7(self):
        """Example from 'Predicate factories'."""

        data = [[1.0, [2, True]], [False, [3]], ['4', {5, True}]]
        strictly_integers = pick(data, is_type(int) & not_type(bool))

        assert list(strictly_integers) == [2, 3, 5]

    def test_example_8(self):
        """Example from 'Built-in predicates'."""

        data = [[], [0], [['1'], b'2']]
        only_values = pick(data, NO_CONTAINERS)

        assert list(only_values) == [0, '1', b'2']

    def test_example_9(self):
        """Examples from 'The values_for_key function'."""

        data = {'node_id': 4,
                'child_nodes': [{'node_id': 8,
                                 'child_nodes': [{'node_id': 16}]},
                                {'node_id': 9}]}
        node_ids = values_for_key(data, key='node_id')

        assert list(node_ids) == [4, 8, 16, 9]

    def test_example_10(self):
        """Examples from 'The max_depth function'."""

        nested_list = [0, [1, [2]]]
        nested_dict = {0: {1: {2: {3: {4: 4}}}}}

        assert max_depth(nested_list) == 2
        assert max_depth(nested_dict) == 4

        assert max_depth([0, [1, []]]) == 2

    def test_example_11(self):
        """Examples from 'Flattening nested data'."""

        data = [[], [0], [[[], 1], [2, [3, [4]], []], [5]]]
        flat_data = pick(data, NO_CONTAINERS)

        assert list(flat_data) == [0, 1, 2, 3, 4, 5]
