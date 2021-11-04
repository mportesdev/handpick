import pytest

from handpick import values_for_key, max_depth
from handpick.core import _iter_depth

from tests import SEQUENCES, SEQS_DICTS, COLLECTIONS


class TestValuesForKey:
    @pytest.mark.parametrize(
        "data, key, expected",
        (
            pytest.param({0: 1, 2: 3}, 0, [1], id="simple"),
            pytest.param({0: 1, 2: 3}, 1, [], id="missing key"),
            pytest.param(
                {"a": {"b": 3, "c": 4}, "b": 1, "c": 2}, "b", [1, 3], id="nested b"
            ),
            pytest.param(
                {"a": {"b": 3, "c": 4}, "b": 1, "c": 2}, "c", [2, 4], id="nested c"
            ),
        ),
    )
    def test_single_key(self, data, key, expected):
        assert list(values_for_key(data, key)) == expected

    @pytest.mark.parametrize(
        "data, keys, expected",
        (
            pytest.param({0: 1, 2: 3}, [0, 2], [1, 3], id="simple"),
            pytest.param({0: 1, 2: 3}, [1, 2], [3], id="missing key"),
            pytest.param(
                {"a": {"b": 3, "c": 4}, "b": 1, "c": 2},
                ["c", "b"],
                [2, 1, 4, 3],
                id="nested",
            ),
            pytest.param(
                {"a": {"b": 3, "c": 4}, "b": 1, "c": 2}, ["b", "d"], [1, 3], id="nested"
            ),
        ),
    )
    def test_list_of_keys(self, data, keys, expected):
        assert list(values_for_key(data, keys)) == expected


class TestMaxDepthIterDepth:
    @pytest.mark.parametrize(
        "root, expected",
        (
            pytest.param(SEQUENCES, 2, id="sequences"),
            pytest.param(SEQS_DICTS, 2, id="seqs & dicts"),
            pytest.param(COLLECTIONS, 3, id="collections"),
            pytest.param([], 0, id="[]"),
            pytest.param([[]], 1, id="[[]]"),
        ),
    )
    def test_max_depth(self, root, expected):
        assert max_depth(root) == expected

    @pytest.mark.parametrize(
        "root, expected",
        (
            pytest.param(SEQUENCES, [0, 1, 2, 2, 1, 2, 2], id="sequences"),
            pytest.param(SEQS_DICTS, [0, 1, 2, 2, 1, 2, 2], id="seqs & dicts"),
            pytest.param(COLLECTIONS, [0, 1, 2, 2, 1, 2, 3, 2], id="collections"),
            pytest.param([], [0], id="[]"),
            pytest.param([[]], [0, 1], id="[[]]"),
        ),
    )
    def test_iter_depth(self, root, expected):
        assert list(_iter_depth(root)) == expected
