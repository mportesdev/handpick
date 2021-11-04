import pytest

from handpick import Predicate, is_type, not_type, IS_COLLECTION, IS_MAPPING

from tests import is_even, is_positive


class TestDecoratorUsage:
    def test_stacked_decorator(self):
        @Predicate
        @Predicate
        def is_even(n):
            return n % 2 == 0

        assert is_even(42) is True
        assert is_even(15) is False
        assert is_even("A") is False  # suppressed TypeError


class TestFromFunctionFactoryMethod:
    @pytest.mark.parametrize("class_or_instance", (Predicate, Predicate(is_even)))
    @pytest.mark.parametrize(
        "function_or_predicate", (is_positive, Predicate(is_positive))
    )
    def test_from_function(self, class_or_instance, function_or_predicate):
        pred = class_or_instance.from_function(function_or_predicate)

        assert pred.__class__ is Predicate

        assert pred(42) is True
        assert pred(0) is False
        assert pred("A") is False  # suppressed TypeError


class TestOverloadedOperators:
    """Test the `&`, `|`, `~` overloaded operations of predicates."""

    def test_predicate_and_predicate(self):
        """Test predicate & predicate."""

        @Predicate
        def is_even(n):
            return n % 2 == 0

        @Predicate
        def is_positive(n):
            return n > 0

        pred = is_even & is_positive

        assert pred(42) is True
        assert pred(-42) is False
        assert pred(15) is False
        assert pred(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_and_function(self):
        """Test predicate & function."""

        @Predicate
        def is_even(n):
            return n % 2 == 0

        def is_positive(n):
            return n > 0

        pred = is_even & is_positive

        assert pred(42) is True
        assert pred(-42) is False
        assert pred(15) is False
        assert pred(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_function_and_predicate(self):
        """Test function & predicate."""

        def is_even(n):
            return n % 2 == 0

        @Predicate
        def is_positive(n):
            return n > 0

        pred = is_even & is_positive

        assert pred(42) is True
        assert pred(-42) is False
        assert pred(15) is False
        assert pred(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_and_non_callable_raises_error(self):
        """Test predicate & non-callable is not implemented."""

        @Predicate
        def is_even(n):
            return n % 2 == 0

        with pytest.raises(TypeError, match="unsupported"):
            is_even & None

    def test_predicate_or_predicate(self):
        """Test predicate | predicate."""

        @Predicate
        def is_even(n):
            return n % 2 == 0

        @Predicate
        def is_positive(n):
            return n > 0

        pred = is_even | is_positive

        assert pred(42) is True
        assert pred(-42) is True
        assert pred(15) is True
        assert pred(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_or_function(self):
        """Test predicate | function."""

        @Predicate
        def is_even(n):
            return n % 2 == 0

        def is_positive(n):
            return n > 0

        pred = is_even | is_positive

        assert pred(42) is True
        assert pred(-42) is True
        assert pred(15) is True
        assert pred(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_function_or_predicate(self):
        """Test function | predicate."""

        def is_even(n):
            return n % 2 == 0

        @Predicate
        def is_positive(n):
            return n > 0

        pred = is_even | is_positive

        assert pred(42) is True
        assert pred(-42) is True
        assert pred(15) is True
        assert pred(-15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_predicate_or_non_callable_raises_error(self):
        """Test predicate | non-callable is not implemented."""

        @Predicate
        def is_even(n):
            return n % 2 == 0

        with pytest.raises(TypeError, match="unsupported"):
            is_even | None

    def test_not_predicate(self):
        """Test ~predicate."""

        @Predicate
        def is_even(n):
            return n % 2 == 0

        pred = ~is_even

        assert pred(42) is False
        assert pred(15) is True
        assert pred("A") is False  # suppressed TypeError

    def test_not_not_predicate(self):
        """Test ~(~predicate)."""

        @Predicate
        def is_even(n):
            return n % 2 == 0

        pred = ~(~is_even)

        assert pred(42) is True
        assert pred(15) is False
        assert pred("A") is False  # suppressed TypeError

    def test_and_or_not(self):
        """Test predicate & (~predicate | predicate)."""

        @Predicate
        def is_even(n):
            return n % 2 == 0

        @Predicate
        def is_positive(n):
            return n > 0

        @Predicate
        def is_palindromic(n):
            return int(str(n)[::-1]) == n

        pred = is_even & (~is_positive | is_palindromic)

        assert pred(-42) is True
        assert pred(252) is True
        assert pred(42) is False
        assert pred(15) is False
        assert pred("A") is False  # suppressed TypeError


class TestPredicateFactories:
    def test_is_type_single_type(self):
        pred = is_type(int)

        assert pred(42) is True
        assert pred(42.15) is False
        assert pred("A") is False

    def test_is_type_tuple_of_types(self):
        pred = is_type((int, float))

        assert pred(42) is True
        assert pred(42.15) is True
        assert pred("A") is False

    def test_not_type_single_type(self):
        pred = not_type(int)

        assert pred(42) is False
        assert pred(42.15) is True
        assert pred("A") is True

    def test_not_type_tuple_of_types(self):
        pred = not_type((int, float))

        assert pred(42) is False
        assert pred(42.15) is False
        assert pred("A") is True


class TestBuiltinPredicates:
    def test_is_collection(self):
        assert IS_COLLECTION({"k": "v"}) is True
        assert IS_COLLECTION([42, 15]) is True
        assert IS_COLLECTION(42) is False

    def test_is_mapping(self):
        assert IS_MAPPING({"k": "v"}) is True
        assert IS_MAPPING([42, 15]) is False
        assert IS_MAPPING(42) is False
