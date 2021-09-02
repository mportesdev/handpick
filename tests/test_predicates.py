import pytest

from handpick import (
    pick,
    Predicate,
    is_type,
    not_type,
    IS_CONTAINER,
    IS_MAPPING,
)

from tests import (
    from_json,
    is_int,
    FLAT,
    DICT_LIST,
    LIST_TUPLE,
    NESTED_DICT,
    LIST_5_LEVELS,
    DICT_5_LEVELS,
)


class TestDecoratorUsage:

    def test_decorator(self):
        ...

    def test_decorator_call(self):
        ...


class TestErrorHandling:

    def test_predicate_suppresses_errors_by_default(self):
        ...

    def test_predicate_propagates_errors_optionally(self):
        ...


class TestFromFunctionFactoryMethod:

    @pytest.mark.parametrize(
        'class_or_instance',
        (
            Predicate,
            Predicate(lambda x: x),
        )
    )
    @pytest.mark.parametrize(
        'function_or_predicate',
        (
            lambda x: x > 0,
            Predicate(lambda x: x > 0)
        )
    )
    def test(self, class_or_instance, function_or_predicate):
        pred = class_or_instance.from_function(function_or_predicate)
        assert isinstance(pred, Predicate)
        assert pred.func is function_or_predicate
        assert not pred(0)
        assert pred(42)
        assert not pred('abc')


class TestOverloadedOperators:
    """Test the `&`, `|`, `~` overloaded operations of predicates."""

    def test_predicate_and_predicate(self):
        """Test predicate & predicate."""

        @Predicate
        def is_str(obj):
            return isinstance(obj, str)

        @Predicate
        def is_short(obj):
            return len(obj) < 3

        short_string = is_str & is_short

        data = [('1', [0, ['py']]), {'f': {(2,), '2'}}, {b'A'}, 'foo',
                {3: 'foo'}]
        result = list(pick(data, short_string))
        assert result == ['1', 'py', '2']

    def test_predicate_and_function(self):
        """Test predicate & function."""

        @Predicate
        def is_tuple(obj):
            return isinstance(obj, tuple)

        tuple_containing_2 = is_tuple & (lambda obj: 2 in obj)

        data = [('2', [2]), {'long': {(2,), '2'}}, range(2), 'long',
                {2: 'long'}]
        result = list(pick(data, tuple_containing_2))
        assert result == [(2,)]

    def test_function_and_predicate(self):
        """Test function & predicate."""

        @Predicate
        def is_list(obj):
            return isinstance(obj, list)

        short_list = (lambda obj: len(obj) < 2) & is_list

        data = [{}, [], '1', [2], {('foo',): []}, [{3}]]
        result = list(pick(data, short_list))
        assert result == [[], [2], [], [{3}]]

    def test_predicate_and_non_callable_raises_error(self):
        """Test predicate & non-callable is not implemented."""

        @Predicate
        def is_dunder_name(string):
            return string.startswith('__') and string.endswith('__')

        with pytest.raises(TypeError):
            is_dunder_name & True

    def test_predicate_or_predicate(self):
        """Test predicate | predicate."""

        @Predicate
        def is_roundable(obj):
            return hasattr(obj, '__round__')

        can_be_int = Predicate(is_int) | is_roundable

        data = [('1', [None, 9.51]), {'': {2., '2'}}, range(5, 7), '2',
                {3: True}]
        result = list(pick(data, can_be_int))
        assert result == [9.51, 2., 5, 6, True]

    def test_predicate_or_function(self):
        """Test predicate | function."""

        @Predicate
        def is_tuple(obj):
            return isinstance(obj, tuple)

        tuple_or_contains_3 = is_tuple | (lambda obj: 3 in obj)

        data = [['1', 3], {'long': {(2,), '2'}}, range(4), 'long', {3: 'long'}]

        result = list(pick(data, tuple_or_contains_3))
        assert result == [['1', 3], (2,), range(4), {3: 'long'}]

    def test_function_or_predicate(self):
        """Test function | predicate."""

        @Predicate
        def is_tuple(obj):
            return isinstance(obj, tuple)

        tuple_or_contains_3 = (lambda obj: 3 in obj) | is_tuple

        data = [['1', 3], {'long': {(2,), '2'}}, range(4), 'long', {3: 'long'}]

        result = list(pick(data, tuple_or_contains_3))
        assert result == [['1', 3], (2,), range(4), {3: 'long'}]

    def test_predicate_or_non_callable_raises_error(self):
        """Test predicate | non-callable is not implemented."""

        @Predicate
        def is_dunder_name(string):
            return string.startswith('__') and string.endswith('__')

        with pytest.raises(TypeError):
            is_dunder_name | True

    def test_not_predicate(self):
        """Test ~predicate."""

        @Predicate
        def is_long(obj):
            return len(obj) > 2

        is_short = ~is_long

        data = [('1', [0, 1], None), {'long': '2'}, range(2), 'long',
                {3, False, 1}]
        result = list(pick(data, is_short))
        assert result == ['1', [0, 1], {'long': '2'}, '2', range(2)]

    def test_compound_predicate(self):
        """Test predicate & (~predicate | ~predicate)."""
        @Predicate
        def is_even(obj):
            return obj % 2 == 0

        falsey = ~Predicate(bool)
        odd_or_zero_int = is_type(int) & (~is_even | falsey)

        data = [[4, [5.0, 11], 3], [[12, [0]], {17: 6}], 9, [[8], 0, {13, '1'}]]
        result = list(pick(data, odd_or_zero_int))
        assert result == [11, 3, 0, 9, 0, 13]

    def test_compound_predicate_with_functions(self):
        """Test (~predicate & ((func & predicate) | (~predicate & func)))."""

        @Predicate
        def is_list_or_dict(obj):
            return isinstance(obj, (list, dict))

        @Predicate
        def is_set(obj):
            return isinstance(obj, set)

        pred = (
            ~is_list_or_dict
            & ((bool & is_type(str)) | (~is_set & (lambda obj: len(obj) > 1)))
        )

        data = (['', 0, ['a']], {0: '', 1: (0, 'b')}, [{1, 2}, b'c'],
                {(), ('\\',)})
        result = list(pick(data, pred))
        assert result == ['a', (0, 'b'), 'b', '\\']


class TestPredicateFactories:

    @pytest.mark.parametrize(
        'data, type_or_types, expected',
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
    def test_is_type_predicate(self, data, type_or_types, expected):
        assert list(pick(data, is_type(type_or_types))) == expected

    @pytest.mark.parametrize(
        'data, type_or_types, expected',
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
    def test_not_type_predicate(self, data, type_or_types, expected):
        assert list(pick(data, not_type(type_or_types))) == expected


class TestBuiltinPredicates:

    @pytest.mark.parametrize(
        'data, expected',
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
    def test_is_container_predicate(self, data, expected):
        assert list(pick(data, ~IS_CONTAINER)) == expected

    @pytest.mark.parametrize(
        'json_file',
        ('list_of_int.json', 'dict_of_int.json')
    )
    def test_is_container_predicate_with_generated_data(self, json_file):
        data = from_json(json_file)
        for n in pick(data, ~IS_CONTAINER):
            assert is_int(n)

    def test_is_mapping_predicate(self):
        ...

    @pytest.mark.parametrize(
        'pred, expected',
        (
            pytest.param(~IS_CONTAINER | IS_MAPPING, [{}, 2, '3', {}, 5]),
            pytest.param(~IS_CONTAINER & IS_MAPPING, []),
        )
    )
    def test_combined_builtin_predicates(self, pred, expected):
        result = list(pick(DICT_LIST, pred))
        assert result == expected
