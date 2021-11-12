import string

import pytest
from hypothesis import given
import hypothesis.strategies as st

from handpick import pick, IS_COLLECTION, is_type, not_type

strings = st.text(string.printable)
keys = strings
values = st.none() | st.booleans() | st.integers() | st.floats() | strings


def containers(children):
    return st.lists(children) | st.dictionaries(keys, children)


nested = st.recursive(values, containers)


@given(nested)
def test_excluded_collections(data):
    picked_1 = pick(data, collections=False)
    picked_2 = pick(data, ~IS_COLLECTION)
    assert list(picked_1) == list(picked_2)


@given(values)
@pytest.mark.parametrize("type_", (str, int))
def test_is_type_not_type(type_, value):
    pred_1 = is_type(type_)
    pred_2 = not_type(type_)
    assert pred_1(value) is (~pred_2)(value)
    assert (~pred_1)(value) is pred_2(value)
