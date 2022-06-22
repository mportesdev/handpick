import pytest

from handpick import (
    Predicate,
    is_type,
    not_type,
    no_error,
    IS_COLLECTION,
    IS_MAPPING,
    INT_STR,
    FLOAT_STR,
    NUM_STR,
)

from tests import is_even, is_positive


class TestDecoratorUsage:
    def test_decorator(self):
        """Test `@Predicate` decorator usage."""
        pred = Predicate(is_even)
        assert pred.func is is_even
        assert pred(42) is pred.func(42) is True
        assert pred(15) is pred.func(15) is False
        assert pred("A") is False  # suppressed TypeError
        with pytest.raises(TypeError):
            pred.func("A")

    def test_decorator_call(self):
        """Test `@Predicate()` decorator usage."""
        pred = Predicate()(is_even)
        assert type(pred) is Predicate
        assert pred.func is is_even
        assert pred(42) is pred.func(42) is True
        assert pred(15) is pred.func(15) is False
        assert pred("A") is False  # suppressed TypeError
        with pytest.raises(TypeError):
            pred.func("A")

    def test_underlying_function_identity(self):
        from_decorator = Predicate(is_even)
        from_decorator_call = Predicate()(is_even)
        assert from_decorator.func is from_decorator_call.func is is_even

    def test_stacked_decorator(self):
        pred = Predicate(Predicate(is_even))
        assert type(pred.func) is Predicate
        assert type(pred.func.func) is not Predicate
        assert pred(42) is pred.func(42) is pred.func.func(42) is True
        assert pred(15) is pred.func(15) is pred.func.func(15) is False
        assert pred("A") is pred.func("A") is False  # suppressed TypeError


class TestFromFunctionFactoryMethod:
    @pytest.mark.parametrize("class_or_instance", (Predicate, Predicate(is_even)))
    @pytest.mark.parametrize(
        "function_or_predicate", (is_positive, Predicate(is_positive))
    )
    def test_from_function(self, class_or_instance, function_or_predicate):
        pred = class_or_instance.from_function(function_or_predicate)

        assert type(pred) is Predicate
        assert pred.func is function_or_predicate
        assert pred(42) is pred.func(42) is True
        assert pred(0) is pred.func(0) is False
        assert pred("A") is False  # suppressed TypeError


class TestOverloadedOperators:
    """Test the `&`, `|`, `~` overloaded operations of predicates."""

    def test_predicate_and_predicate(self):
        """Test predicate & predicate."""
        _is_even = Predicate(is_even)
        _is_positive = Predicate(is_positive)
        pred = _is_even & _is_positive

        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is False
        assert pred(15) is pred.func(15) is False
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_and_function(self):
        """Test predicate & function."""
        _is_even = Predicate(is_even)
        pred = _is_even & is_positive

        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is False
        assert pred(15) is pred.func(15) is False
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_function_and_predicate(self):
        """Test function & predicate."""
        _is_positive = Predicate(is_positive)
        pred = is_even & _is_positive

        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is False
        assert pred(15) is pred.func(15) is False
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_and_non_callable_raises_error(self):
        """Test predicate & non-callable is not implemented."""
        _is_even = Predicate(is_even)
        with pytest.raises(TypeError, match="unsupported"):
            _is_even & None

    def test_predicate_or_predicate(self):
        """Test predicate | predicate."""
        _is_even = Predicate(is_even)
        _is_positive = Predicate(is_positive)
        pred = _is_even | _is_positive

        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is True
        assert pred(15) is pred.func(15) is True
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_or_function(self):
        """Test predicate | function."""
        _is_even = Predicate(is_even)
        pred = _is_even | is_positive

        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is True
        assert pred(15) is pred.func(15) is True
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_function_or_predicate(self):
        """Test function | predicate."""
        _is_positive = Predicate(is_positive)
        pred = is_even | _is_positive

        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is True
        assert pred(15) is pred.func(15) is True
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_or_non_callable_raises_error(self):
        """Test predicate | non-callable is not implemented."""
        _is_even = Predicate(is_even)
        with pytest.raises(TypeError, match="unsupported"):
            _is_even | None

    def test_not_predicate(self):
        """Test ~predicate."""
        _is_even = Predicate(is_even)
        pred = ~_is_even

        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is False
        assert pred(15) is pred.func(15) is True
        assert pred("A") is False  # suppressed TypeError

    def test_not_not_predicate(self):
        """Test ~(~predicate)."""
        _is_even = Predicate(is_even)
        pred = ~(~_is_even)

        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(15) is pred.func(15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_and_or_not(self):
        """Test predicate & (~predicate | predicate)."""
        _is_even = Predicate(is_even)
        _is_positive = Predicate(is_positive)

        @Predicate
        def is_palindromic(n):
            return int(str(n)[::-1]) == n

        pred = _is_even & (~_is_positive | is_palindromic)

        assert type(pred.func) is not Predicate
        assert pred(-42) is pred.func(-42) is True
        assert pred(252) is pred.func(252) is True
        assert pred(42) is pred.func(42) is False
        assert pred(15) is pred.func(15) is False
        assert pred("A") is False  # suppressed TypeError


class TestPredicateFactories:
    def test_is_type_single_type(self):
        pred = is_type(int)

        assert isinstance(pred, Predicate)
        assert pred(42) is True
        assert pred(42.15) is False
        assert pred("A") is False

    def test_is_type_tuple_of_types(self):
        pred = is_type((int, float))

        assert isinstance(pred, Predicate)
        assert pred(42) is True
        assert pred(42.15) is True
        assert pred("A") is False

    def test_not_type_single_type(self):
        pred = not_type(int)

        assert isinstance(pred, Predicate)
        assert pred(42) is False
        assert pred(42.15) is True
        assert pred("A") is True

    def test_not_type_tuple_of_types(self):
        pred = not_type((int, float))

        assert isinstance(pred, Predicate)
        assert pred(42) is False
        assert pred(42.15) is False
        assert pred("A") is True

    def test_no_error_int(self):
        pred = no_error(int)

        assert isinstance(pred, Predicate)
        assert pred("42") is True
        assert pred("4.2") is False
        assert pred([]) is False

    def test_no_error_len(self):
        pred = no_error(len)

        assert isinstance(pred, Predicate)
        assert pred("A") is True
        assert pred([]) is True
        assert pred(42) is False


class TestBuiltinPredicates:
    def test_is_collection(self):
        assert IS_COLLECTION({"k": "v"}) is True
        assert IS_COLLECTION([42, 15]) is True
        assert IS_COLLECTION(42) is False

    def test_is_mapping(self):
        assert IS_MAPPING({"k": "v"}) is True
        assert IS_MAPPING([42, 15]) is False
        assert IS_MAPPING(42) is False

    def test_int_str(self):
        assert INT_STR("42") is True
        assert INT_STR("4.2") is False
        assert INT_STR("1.5e3") is False
        assert INT_STR("inf") is False
        assert INT_STR("nan") is False
        assert INT_STR("4+2j") is False

        assert INT_STR("A") is False
        assert INT_STR(42) is False
        assert INT_STR(4.2) is False
        assert INT_STR(1.5e3) is False
        assert INT_STR(4 + 2j) is False

    def test_float_str(self):
        assert FLOAT_STR("42") is True
        assert FLOAT_STR("4.2") is True
        assert FLOAT_STR("1.5e3") is True
        assert FLOAT_STR("inf") is True
        assert FLOAT_STR("nan") is True
        assert FLOAT_STR("4+2j") is False

        assert FLOAT_STR("A") is False
        assert FLOAT_STR(42) is False
        assert FLOAT_STR(4.2) is False
        assert FLOAT_STR(1.5e3) is False
        assert FLOAT_STR(4 + 2j) is False

    def test_num_str(self):
        assert NUM_STR("42") is True
        assert NUM_STR("4.2") is True
        assert NUM_STR("1.5e3") is True
        assert NUM_STR("inf") is True
        assert NUM_STR("nan") is True
        assert NUM_STR("4+2j") is True

        assert NUM_STR("A") is False
        assert NUM_STR(42) is False
        assert NUM_STR(4.2) is False
        assert NUM_STR(1.5e3) is False
        assert NUM_STR(4 + 2j) is False
