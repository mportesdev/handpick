import pytest

from handpick import values_for_key, max_depth
from handpick.core import _iter_depth

from tests import (
    from_json,
    FLAT,
    NESTED_LIST,
    DICT_LIST,
    LIST_TUPLE,
    NESTED_DICT,
    LIST_5_LEVELS,
    DICT_5_LEVELS,
)


class TestValuesForKey:
    @pytest.mark.parametrize(
        "data, key, expected",
        (
            pytest.param({}, 0, [], id="empty"),
            pytest.param({0: 1, 2: 3}, 0, [1], id="top-level key 0"),
            pytest.param({0: 1, 2: 3}, 1, [], id="top-level key missing"),
            pytest.param({0: {0: 1}}, 0, [{0: 1}, 1], id="same key, nested"),
            pytest.param({0: {1: 2}, 3: {1: 4}}, 1, [2, 4], id="same key, same level"),
            pytest.param(
                {"a": {"b": 0}, "b": 1}, "b", [1, 0], id="same key different level"
            ),
            pytest.param(
                [
                    {
                        "foo": [{"x": 1, "y": 2}, {"x": 3, "y": 4}],
                        "bar": ({"x": 5}, {"x": 6}),
                    }
                ],
                "x",
                [1, 3, 5, 6],
                id="list-dict-tuple x",
            ),
            pytest.param(
                [
                    {
                        "foo": [{"x": 1, "y": 2}, {"x": 3, "y": 4}],
                        "bar": ({"x": 5}, {"x": 6}),
                    }
                ],
                "y",
                [2, 4],
                id="list-dict-tuple y",
            ),
        ),
    )
    def test_single_key(self, data, key, expected):
        assert list(values_for_key(data, key)) == expected

    @pytest.mark.parametrize(
        "data, keys, expected",
        (
            pytest.param({}, [], [], id="empty"),
            pytest.param({}, [0], [], id="empty key 0"),
            pytest.param({0: 1, 2: 3}, [0, 2], [1, 3], id="top-level keys 0, 2"),
            pytest.param({0: 1, 2: 3}, [1, 2], [3], id="top-level key missing"),
            pytest.param(
                {0: {1: 2}, 3: {1: 4}},
                [1, 3],
                [{1: 4}, 2, 4],
                id="two keys, two levels",
            ),
            pytest.param(
                [
                    {
                        "foo": [{"x": 1, "y": 2}, {"x": 3, "y": 4}],
                        "bar": ({"x": 5}, {"x": 6}),
                    }
                ],
                ["x", "y"],
                [1, 2, 3, 4, 5, 6],
                id="list-dict-tuple keys x, y",
            ),
        ),
    )
    def test_list_of_keys(self, data, keys, expected):
        assert list(values_for_key(data, keys)) == expected

    @pytest.mark.parametrize(
        "key, expected",
        (
            pytest.param("-98", [2532, 29553]),
            pytest.param("16399", [20528]),
        ),
    )
    def test_values_for_key_with_generated_data(self, key, expected):
        data = from_json("dict_of_int.json")
        assert list(values_for_key(data, key)) == expected


class TestMaxDepthIterDepth:
    @pytest.mark.parametrize(
        "root, expected",
        (
            pytest.param(FLAT, 1, id="flat"),
            pytest.param(NESTED_LIST, 3, id="nested_list"),
            pytest.param(DICT_LIST, 3, id="dict_list"),
            pytest.param(LIST_TUPLE, 3, id="list_tuple"),
            pytest.param(NESTED_DICT, 5, id="nested_dict"),
            pytest.param(LIST_5_LEVELS, 4, id="list_5_levels"),
            pytest.param(DICT_5_LEVELS, 4, id="dict_5_levels"),
            pytest.param([], 0, id="[]"),
            pytest.param([[]], 1, id="[[]]"),
            pytest.param([[[]]], 2, id="[[[]]]"),
        ),
    )
    def test_max_depth(self, root, expected):
        assert max_depth(root) == expected

    @pytest.mark.parametrize(
        "json_file, expected",
        (
            pytest.param("list_of_int.json", 12),
            pytest.param("dict_of_int.json", 5),
        ),
    )
    def test_max_depth_with_generated_data(self, json_file, expected):
        root = from_json(json_file)
        assert max_depth(root) == expected

    @pytest.mark.parametrize(
        "root, expected",
        (
            pytest.param(FLAT, [0, 1, 1], id="flat"),
            pytest.param(NESTED_LIST, [0, 1, 1, 2, 3], id="nested_list"),
            pytest.param(DICT_LIST, [0, 1, 2, 2, 1, 2, 2, 3], id="dict_list"),
            pytest.param(LIST_TUPLE, [0, 1, 2, 3, 1], id="list_tuple"),
            pytest.param(
                NESTED_DICT,
                [0, 1, 2, 3, 3, 2, 3, 4, 5, 1, 2, 3, 3, 2, 3, 3, 3],
                id="nested_dict",
            ),
            pytest.param(
                LIST_5_LEVELS, [0, 1, 2, 3, 4, 1, 2, 3, 2], id="list_5_levels"
            ),
            pytest.param(DICT_5_LEVELS, [0, 1, 2, 3, 4, 4], id="dict_5_levels"),
            pytest.param([], [0], id="[]"),
            pytest.param([[]], [0, 1], id="[[]]"),
            pytest.param([[[]]], [0, 1, 2], id="[[[]]]"),
        ),
    )
    def test_iter_depth(self, root, expected):
        assert list(_iter_depth(root)) == expected
