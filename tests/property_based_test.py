import string

from hypothesis import given
import hypothesis.strategies as st

from handpick import pick, Predicate, IS_COLLECTION, is_type, not_type

from tests import is_even

strings = st.text(string.printable)
keys = strings
values = st.none() | st.booleans() | st.integers() | st.floats() | strings


def collections(children):
    return st.lists(children) | st.dictionaries(keys, children)


nested = st.recursive(values, collections)


@given(nested)
def test_excluded_collections(data):
    picked_1 = pick(data, collections=False)
    picked_2 = pick(data, ~IS_COLLECTION)
    assert list(picked_1) == list(picked_2)


types = st.sampled_from((bool, int, float, str, list, dict))
values_and_collections = values | collections(values)


@given(types, values_and_collections)
def test_is_type_not_type(type_, value):
    pred_1 = is_type(type_)
    pred_2 = not_type(type_)
    assert pred_1(value) is (~pred_2)(value)
    assert (~pred_1)(value) is pred_2(value)


@given(values)
def test_predicate_decorator_call(value):
    pred_1 = Predicate(is_even)
    pred_2 = Predicate()(is_even)
    assert pred_1(value) is pred_2(value)
