import functools
import itertools
import operator

import pytest

from handpick import pick, Predicate, IS_CONTAINER

from tests import (
    is_int,
    FLAT,
    NESTED_LIST,
    DICT_LIST,
    LIST_TUPLE,
    NESTED_DICT,
    LIST_5_LEVELS,
    DICT_5_LEVELS,
)


def is_str(obj):
    return isinstance(obj, str)


def is_tuple(obj):
    return isinstance(obj, tuple)


def retrieve_items(obj, routes):
    yield from (
        functools.reduce(operator.getitem, [obj, *route])
        for route in routes
    )


class TestPick:

    @pytest.mark.parametrize(
        'data, pred, routes',
        (
            pytest.param(FLAT,
                         Predicate(lambda obj: float(obj) < 50),
                         [[1], [2]],
                         id='flat - float < 50'),
            pytest.param(NESTED_LIST,
                         Predicate(lambda obj: obj[1]),
                         [[0], [1], [1, 1], [1, 2]],
                         id='nested list - item 3'),
            pytest.param(LIST_TUPLE,
                         Predicate(lambda obj: 3 in obj),
                         [[0, 1], [0, 1, 0]],
                         id='list tuple - contains 3'),
            pytest.param(NESTED_DICT,
                         lambda obj: isinstance(obj, dict) and not obj,
                         [['1', 'list', 1, 1, 1], ['2', 'tuple', 0]],
                         id='nested dict - empty dict'),
        )
    )
    def test_picked_objects_by_identity(self, data, pred, routes):
        result = pick(data, pred)
        expected_items = retrieve_items(data, routes)

        # Unique object to make the assertion fail if `actual` and
        # `expected` are of unequal length
        sentinel = object()

        for actual, expected in itertools.zip_longest(result, expected_items,
                                                      fillvalue=sentinel):
            assert actual is expected


class TestContainerHandling:

    def test_containers_included_by_default(self):
        ...

    @pytest.mark.parametrize(
        'data, expected',
        (
                pytest.param(LIST_5_LEVELS,
                             [bytearray(b'2'), '4', 3.5, b'1', '0', '2',
                              b'3', '1',
                              2],
                             id='list 5 levels - no containers'),
                pytest.param(DICT_5_LEVELS,
                             ['0_value1', '2_value1', '4_value', '4_value2',
                              '1_value2'],
                             id='dict 5 levels - no containers'),
        )
    )
    def test_containers_excluded_optionally(self, data, expected):
        assert list(
            pick(data, lambda x: True, containers=False)) == expected

    def test_containers_in_dict_keys_included_by_default(self):
        ...

    def test_containers_in_dict_keys_excluded_optionally(self):
        data = {'1': (), (0, 1): 2}
        result = pick(data, lambda x: True, containers=False,
                      dict_keys=True)

        assert list(result) == ['1', 0, 1, 2]


class TestFunctionsAndPredicates:

    @pytest.mark.parametrize(
        'data, pred, expected',
        (
            pytest.param(FLAT, bool, [62, True, 'food', 'foo'],
                         id='flat - bool'),
            pytest.param(NESTED_LIST, bool,
                         [[1, 2, 100.0], 1, 2, 100.0, [3, 'Py', [{}, 4], 5],
                          3, 'Py', [{}, 4], 4, 5],
                         id='nested dict - is list'),
            pytest.param(FLAT, is_str, ['food', '', 'foo'],
                         id='flat - is str'),
            pytest.param(LIST_TUPLE, is_tuple,
                         [((1, 2, 3), 3), (1, 2, 3), ('foo', 'bar')],
                         id='list tuple - is tuple'),
            pytest.param(NESTED_LIST, is_int, [1, 2, 3, 4, 5],
                         id='nested list - is int'),
            pytest.param(FLAT, lambda obj: hasattr(obj, 'count'),
                         ['food', '', [], 'foo'],
                         id='flat - has .count'),
            pytest.param(NESTED_DICT, lambda obj: hasattr(obj, 'append'),
                         [[], [1, [2, [3, {}]]], [2, [3, {}]], [3, {}], [], []],
                         id='nested dict - has .append'),
            pytest.param(NESTED_DICT,
                         lambda obj: isinstance(obj, dict) and not obj,
                         [{}, {}],
                         id='nested dict - empty dict'),
        )
    )
    def test_safe_function(self, data, pred, expected):
        assert list(pick(data, pred)) == expected

    @pytest.mark.parametrize(
        'data, pred, expected_error',
        (
            pytest.param(FLAT,
                         lambda obj: float(obj) < 50,
                         (TypeError, ValueError),
                         id='flat - float < 50'),
            pytest.param(LIST_5_LEVELS,
                         lambda obj: int(obj) >= 0,
                         (TypeError, ValueError),
                         id='list 5 levels - int >= 0'),
            pytest.param(FLAT,
                         lambda obj: obj[2],
                         (TypeError, IndexError, KeyError),
                         id='flat - item 2'),
            pytest.param(NESTED_LIST,
                         lambda obj: obj[1],
                         (TypeError, IndexError, KeyError),
                         id='nested list - item 3'),
            pytest.param(FLAT,
                         lambda obj: len(obj) == 0,
                         TypeError,
                         id='flat - len 0'),
            pytest.param(LIST_TUPLE,
                         lambda obj: len(obj) == 3,
                         TypeError,
                         id='list tuple - len 3'),
            pytest.param(FLAT,
                         lambda obj: 'foo' in obj,
                         TypeError,
                         id='flat - contains "foo"'),
            pytest.param(LIST_TUPLE,
                         lambda obj: 3 in obj,
                         TypeError,
                         id='list tuple - contains 3'),
            pytest.param(FLAT,
                         lambda obj: obj % 2 == 0,
                         TypeError,
                         id='flat - even number'),
        )
    )
    def test_function_raises_error(self, data, pred, expected_error):
        with pytest.raises(expected_error):
            list(pick(data, pred))

    @pytest.mark.parametrize(
        'data, pred, expected',
        (
            pytest.param(FLAT,
                         Predicate(lambda obj: float(obj) < 50),
                         [0.0, True],
                         id='flat - float < 50'),
            pytest.param(LIST_5_LEVELS,
                         Predicate(lambda obj: int(obj) >= 0),
                         [bytearray(b'2'), '4', 3.5, b'1', '0', '2', b'3',
                          '1', 2],
                         id='list 5 levels - int >= 0'),
            pytest.param(FLAT,
                         Predicate(lambda obj: obj[2]),
                         ['food', 'foo'],
                         id='flat - item 2'),
            pytest.param(NESTED_LIST,
                         Predicate(lambda obj: obj[1]),
                         [[1, 2, 100.0], [3, 'Py', [{}, 4], 5], 'Py', [{}, 4]],
                         id='nested list - item 3'),
            pytest.param(FLAT,
                         Predicate(lambda obj: len(obj) == 0),
                         ['', [], {}],
                         id='flat - len 0'),
            pytest.param(LIST_TUPLE,
                         Predicate(lambda obj: len(obj) == 3),
                         [[None, ((1, 2, 3), 3), 0], (1, 2, 3), 'foo', 'bar'],
                         id='list tuple - len 3'),
            pytest.param(FLAT,
                         Predicate(lambda obj: 'foo' in obj),
                         ['food', 'foo'],
                         id='flat - contains "foo"'),
            pytest.param(LIST_TUPLE,
                         Predicate(lambda obj: 3 in obj),
                         [((1, 2, 3), 3), (1, 2, 3)],
                         id='list tuple - contains 3'),
            pytest.param(FLAT,
                         Predicate(lambda obj: obj % 2 == 0),
                         [62, 0.0],
                         id='flat - even number'),
        )
    )
    def test_predicate_supresses_error(self, data, pred, expected):
        assert list(pick(data, pred)) == expected


class TestDictKeyHandling:

    STRINGS = ['foot', ['', 'foobar'], {'foo': 'bar', 'bar': 'fool'},
               'good food']

    @pytest.mark.parametrize(
        'data, pred, expected',
        (
            pytest.param(STRINGS, is_str,
                         ['foot', '', 'foobar', 'bar', 'fool', 'good food'],
                         id='strings - is str'),
            pytest.param(STRINGS, lambda obj: 'foo' in obj,
                         ['foot', 'foobar', {'foo': 'bar', 'bar': 'fool'},
                          'fool', 'good food'],
                         id='strings - contains "foo"'),
            pytest.param(DICT_LIST, Predicate(lambda n: 2 <= n <= 4), [2],
                         id='dict list - 2-4'),
            pytest.param(NESTED_DICT, is_str, [], id='nested dict - is str'),
        )
    )
    def test_dict_keys_excluded_by_default(self, data, pred, expected):
        assert list(pick(data, pred)) == expected

    @pytest.mark.parametrize(
        'data, pred, expected',
        (
            pytest.param(STRINGS, is_str,
                         ['foot', '', 'foobar', 'foo', 'bar', 'bar', 'fool',
                          'good food'],
                         id='strings - is str'),
            pytest.param(STRINGS, lambda obj: 'foo' in obj,
                         ['foot', 'foobar', {'foo': 'bar', 'bar': 'fool'},
                          'foo', 'fool', 'good food'],
                         id='strings - contains "foo"'),
            pytest.param(DICT_LIST, Predicate(lambda n: 2 <= n <= 4), [2, 4],
                         id='dict list - 2-4'),
            pytest.param(NESTED_DICT, is_str,
                         ['1', 'dict', 'list', 'tuple', 'list', '2', 'dict',
                          'list', 'tuple', 'tuple'],
                         id='nested dict - is str'),
        )
    )
    def test_dict_keys_included_optionally(self, data, pred, expected):
        assert list(pick(data, pred, dict_keys=True)) == expected


class TestSpecialCases:

    @pytest.mark.parametrize('pred', (lambda x: True, bool, abs))
    @pytest.mark.parametrize('data', ([], (), {}))
    def test_empty_root_yields_nothing(self, data, pred):
        assert list(pick(data, pred)) == []

    @pytest.mark.parametrize('pred', (lambda x: True, bool, abs))
    @pytest.mark.parametrize('data', (0, None, hash))
    def test_non_iterable_root_yields_nothing(self, data, pred):
        assert list(pick(data, pred)) == []

    @pytest.mark.parametrize(
        'data, pred, expected_len',
        (
            pytest.param([1, 2, 3], 1, 1, id='1'),
            pytest.param([1, 2, 3], None, 0, id='None'),
            pytest.param([[1, 2], [2, 3]], 2, 2, id='2'),
            pytest.param(DICT_LIST, {}, 2, id='dict list - {}'),
        )
    )
    def test_non_callable_predicate(self, data, pred, expected_len):
        assert list(pick(data, pred)) == [pred] * expected_len


class TestStringsAndBytesLike:

    @pytest.mark.parametrize(
        'data, expected',
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
    def test_strings_not_iterated_by_default(self, data, expected):
        assert list(pick(data, is_str)) == expected

    @pytest.mark.parametrize(
        'data, expected',
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
    def test_strings_iterated_optionally(self, data, expected):
        assert list(pick(data, is_str, strings=True)) == expected

    @pytest.mark.parametrize(
        'data, expected',
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
    def test_bytes_like_not_iterated_by_default(self, data, expected):
        assert list(pick(data, is_int)) == expected

    @pytest.mark.parametrize(
        'data, expected',
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
    def test_bytes_like_iterated_optionally(self, data, expected):
        assert list(pick(data, is_int, bytes_like=True)) == expected


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
        assert list(pick(data, ~IS_CONTAINER)) == expected
