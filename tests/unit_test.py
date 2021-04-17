import functools
import itertools
import json
import operator
from pathlib import Path

import pytest

from handpick import (
    pick,
    predicate,
    ALL,
    NO_CONTAINERS,
    NO_LIST_DICT,
    is_type,
    not_type,
    flat,
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
            pytest.param(['str'], ['str'], id='flat'),
            pytest.param((['ab'], 'cd'), ['ab', 'cd'], id='nested'),
            pytest.param({'ef': 'gh'}, ['ef', 'gh'], id='dict'),
            pytest.param('str', [], id='str'),
        )
    )
    def test_strings_not_iterated_by_default(self, root, expected):
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
    def test_strings_iterated_optionally(self, root, expected):
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
    def test_bytes_like_not_iterated_by_default(self, root, expected):
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
    def test_bytes_like_iterated_optionally(self, root, expected):
        result = list(pick(root, is_int, dict_keys=True, bytes_like=True))
        assert result == expected


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
        def is_set(obj):
            return isinstance(obj, set)

        pred = (
            NO_LIST_DICT
            & ((bool & is_type(str)) | (~is_set & (lambda obj: len(obj) > 1)))
        )

        root = (['', 0, ['a']], {0: '', 1: (0, 'b')}, [{1, 2}, b'c'],
                {(), ('\\',)})
        result = list(pick(root, pred))
        assert result == ['a', (0, 'b'), 'b', '\\']


class TestMaxDepth:

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


class TestIterDepth:

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
        )
    )
    def test_iter_depth(self, root, expected):
        assert list(_iter_depth(root)) == expected


class TestBuiltinPredicates:

    @pytest.mark.parametrize(
        'root, expected',
        (
            pytest.param(FLAT, list(FLAT), id='flat - all'),
            pytest.param(DICT_LIST,
                         [[{}, (2, '3')], {}, (2, '3'), 2, '3',
                          [{}, [5, ()]], {}, [5, ()], 5, ()],
                         id='dict list - all'),
        )
    )
    def test_all_predicate(self, root, expected):
        assert list(pick(root, ALL)) == expected

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
        'root, expected',
        (
            pytest.param(DICT_LIST, [(2, '3'), 2, '3', 5, ()],
                         id='dict list - no list/dict'),
            pytest.param(LIST_5_LEVELS,
                         [bytearray(b'2'), '4', 3.5, b'1', '0', '2', b'3', '1',
                          (2,), 2],
                         id='list 5 levels - no list/dict'),
            pytest.param(DICT_5_LEVELS,
                         ['0_value1', '2_value1', '4_value', {'4_value2'},
                          '4_value2', '1_value2'],
                         id='dict 5 levels - no list/dict'),
        )
    )
    def test_no_list_dict_predicate(self, root, expected):
        assert list(pick(root, NO_LIST_DICT)) == expected

    @pytest.mark.parametrize(
        'json_file',
        ('list_of_int.json', 'dict_of_int.json')
    )
    def test_no_list_dict_predicate_with_generated_data(self, json_file):
        root = from_json(json_file)
        for n in pick(root, NO_LIST_DICT):
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
        no_dict_or_array = NO_LIST_DICT & not_type(tuple)
        no_str_or_binary = ~is_type((str, bytes, bytearray))

        root = LIST_5_LEVELS
        result = list(pick(root, no_dict_or_array & no_str_or_binary))
        assert result == [3.5, 2]


class TestFlat:

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
    def test_flat(self, data, expected):
        assert list(flat(data)) == expected


class TestReadmeExamples:
    """Test examples from README."""

    DICT = {
        'key': {'str': 'Py', 'n': 1},
        '_key': {'_str': '_Py', '_n': 2}
    }

    LIST = [
        [4, [5.0, 1], 3.0],
        [[15, []], {17: 7}],
        9,
        [[8], 0, {13, ''}],
        97
    ]

    LIST_OF_INT = [[], [0], [[[], 1], [2, [3, [4]], []], [5]]]

    @pytest.mark.parametrize(
        'predicate, expected',
        (
            pytest.param(lambda n: n > 3, [100.0, 4, 5],
                         id='> 3'),
            pytest.param(lambda n: n > 3 and isinstance(n, int), [4, 5],
                         id='int > 3'),
            pytest.param(lambda seq: len(seq) == 2, ['Py', [{}, 4]],
                         id='len 2'),
        )
    )
    def test_example_1(self, predicate, expected):
        root = NESTED_LIST
        assert list(pick(root, predicate)) == expected

    def test_example_2(self):
        root = [1, [1., [2, 1]], [{'id': 1, 'data': [0, 1.0]}, 1, [{}, [1]], 0]]
        ones = pick(root, 1)

        assert len(list(ones)) == 7

    @pytest.mark.parametrize(
        'dict_keys, expected',
        (
            pytest.param(False, ['_Py'], id='no keys'),
            pytest.param(True, ['_key', '_str', '_Py', '_n'],
                         id='including keys'),
        )
    )
    def test_example_3(self, dict_keys, expected):
        root = self.DICT
        data = pick(root, lambda s: s.startswith('_'), dict_keys)

        assert list(data) == expected

    def test_example_4(self):
        @predicate
        def is_int(n):
            return isinstance(n, int)

        @predicate
        def is_even(n):
            return n % 2 == 0

        root = self.LIST

        non_even_int = is_int & ~is_even
        odd_integers = pick(root, non_even_int)

        assert list(odd_integers) == [1, 15, 7, 9, 13, 97]

    def test_example_5(self):
        @predicate
        def is_list(obj):
            return isinstance(obj, list)

        root = [('1', [2]), {('x',): [(3, [4]), '5']}, ['x', [['6']]],
                {7: ('x',)}]

        short_list = (lambda obj: len(obj) < 2) & is_list
        short_lists = pick(root, short_list)

        assert list(short_lists) == [[2], [4], [['6']], ['6']]

    def test_example_6(self):
        data = self.LIST_OF_INT
        flat_data = pick(data, NO_CONTAINERS)

        assert list(flat_data) == [0, 1, 2, 3, 4, 5]

    def test_example_7(self):
        data = self.LIST_OF_INT
        flat_data = flat(data)
        assert list(flat_data) == [0, 1, 2, 3, 4, 5]

    def test_example_8(self):
        root = [[1.0, [2, True], False], [False, [3]], [[4.5], '6', {7, True}]]
        integers_only = pick(root, is_type(int) & not_type(bool))

        assert list(integers_only) == [2, 3, 7]
