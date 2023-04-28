import string

import hypothesis.strategies as st
from hypothesis import given

from handpick import Predicate
from . import is_even

strings = st.text(string.printable)
values = st.none() | st.booleans() | st.integers() | st.floats() | strings


def _same_result_or_error(predicate_1, predicate_2, arg):
    try:
        result_1 = predicate_1(arg)
    except Exception as e:
        result_1 = e
    try:
        result_2 = predicate_2(arg)
    except Exception as e:
        result_2 = e
    # same bool returned or same error raised
    return result_1 is result_2 or (
        type(result_1) is type(result_2) and result_1.args == result_2.args
    )


pred = Predicate(is_even)
pred_call = Predicate()(is_even)
pred_errors = Predicate(is_even, suppressed_errors=())
pred_call_errors = Predicate(suppressed_errors=())(is_even)


@given(values)
def test_predicate_decorator_vs_decorator_call(value):
    assert _same_result_or_error(pred, pred_call, value)
    assert _same_result_or_error(pred_errors, pred_call_errors, value)
