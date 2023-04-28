import pytest

from handpick import (
    Predicate,
    is_type,
    no_error,
)
from . import is_even, is_positive, first_item_positive, palindromic_int


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

    def test_stacked_decorator(self):
        pred = Predicate(Predicate(is_even))
        assert type(pred.func) is Predicate
        assert type(pred.func.func) is not Predicate
        assert pred(42) is pred.func(42) is pred.func.func(42) is True
        assert pred(15) is pred.func(15) is pred.func.func(15) is False
        assert pred("A") is pred.func("A") is False  # suppressed TypeError


class TestErrorHandling:
    def test_predicate_suppresses_errors_by_default(self):
        pred = Predicate(first_item_positive)
        assert type(pred) is Predicate
        assert pred([42]) is pred.func([42]) is True
        assert pred([-15]) is pred.func([-15]) is False
        # suppressed IndexError and TypeError
        assert pred([]) is False
        assert pred(["A"]) is False

    def test_predicate_propagates_errors_optionally(self):
        pred = Predicate(suppressed_errors=())(first_item_positive)
        assert type(pred) is Predicate
        assert pred([42]) is pred.func([42]) is True
        assert pred([-15]) is pred.func([-15]) is False
        # propagated IndexError and TypeError
        with pytest.raises(IndexError):
            pred([])
        with pytest.raises(TypeError):
            pred(["A"])


class TestOverloadedOperators:
    """Test the `&`, `|`, `~` overloaded operations of predicates."""

    def test_predicate_and_predicate(self):
        """Test predicate & predicate."""
        pred = Predicate(is_even) & Predicate(is_positive)
        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is False
        assert pred(15) is pred.func(15) is False
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_and_function(self):
        """Test predicate & function."""
        pred = Predicate(is_even) & is_positive
        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is False
        assert pred(15) is pred.func(15) is False
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_function_and_predicate(self):
        """Test function & predicate."""
        pred = is_even & Predicate(is_positive)
        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is False
        assert pred(15) is pred.func(15) is False
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_and_non_callable_raises_error(self):
        """Test predicate & non-callable is not implemented."""
        pred = Predicate(is_even)
        with pytest.raises(TypeError, match="unsupported"):
            pred & None

    def test_predicate_or_predicate(self):
        """Test predicate | predicate."""
        pred = Predicate(is_even) | Predicate(is_positive)
        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is True
        assert pred(15) is pred.func(15) is True
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_or_function(self):
        """Test predicate | function."""
        pred = Predicate(is_even) | is_positive
        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is True
        assert pred(15) is pred.func(15) is True
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_function_or_predicate(self):
        """Test function | predicate."""
        pred = is_even | Predicate(is_positive)
        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(-42) is pred.func(-42) is True
        assert pred(15) is pred.func(15) is True
        assert pred(-15) is pred.func(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_or_non_callable_raises_error(self):
        """Test predicate | non-callable is not implemented."""
        pred = Predicate(is_even)
        with pytest.raises(TypeError, match="unsupported"):
            pred | None

    def test_not_predicate(self):
        """Test ~predicate."""
        pred = ~Predicate(is_even)
        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is False
        assert pred(15) is pred.func(15) is True
        assert pred("A") is False  # suppressed TypeError

    def test_not_not_predicate(self):
        """Test ~~predicate."""
        pred = ~~Predicate(is_even)
        assert type(pred.func) is not Predicate
        assert pred(42) is pred.func(42) is True
        assert pred(15) is pred.func(15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_and_or_not(self):
        """Test predicate & (~predicate | predicate)."""
        pred = Predicate(is_even) & (
            ~Predicate(is_positive) | Predicate(palindromic_int)
        )
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
