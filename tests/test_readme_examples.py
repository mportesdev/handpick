from handpick import (
    pick,
    Predicate,
    is_type,
    NUM_STR,
    values_for_key,
    max_depth,
)


class TestReadmeExamples:
    """Test examples from README."""

    def test_example_simple_predicate(self):
        def is_non_empty_string(obj):
            return isinstance(obj, str) and obj

        data = [[1, ""], [-2, ["foo", 3.0]], -4, "bar"]
        assert list(pick(data, is_non_empty_string)) == ["foo", "bar"]

    def test_example_dict_keys(self):
        data = {"foo": {"name": "foo"}, "bar": {"name": "bar"}}
        assert list(pick(data, lambda obj: "a" in obj)) == ["bar"]
        assert list(pick(data, lambda obj: "a" in obj, dict_keys=True)) == [
            "name",
            "bar",
            "name",
            "bar",
        ]

    def test_example_combining_predicates(self):
        @Predicate
        def is_integer(obj):
            return isinstance(obj, int)

        @Predicate
        def is_even(number):
            return number % 2 == 0

        data = [[4, [5.0, 1], 3.0], [[15, []], {17: [7, [8], 0]}]]
        odd_int = is_integer & ~is_even
        assert list(pick(data, odd_int)) == [1, 15, 7]

    def test_example_predicates_with_functions(self):
        @Predicate
        def is_list(obj):
            return isinstance(obj, list)

        data = [("1", [2]), {("x",): [(3, [4]), "5"]}, ["x", ["6"]], {7: ("x",)}]
        short_list = (lambda obj: len(obj) < 2) & is_list
        assert list(pick(data, short_list)) == [[2], [4], ["6"]]

    def test_example_suppressing_errors(self):
        @Predicate
        def above_zero(number):
            return number > 0

        assert above_zero(1) is True
        assert above_zero("a") is False
        assert list(pick([[1, "Py", -2], [None, 3.0]], above_zero)) == [1, 3.0]

    def test_example_predicate_factories(self):
        data = [[1.0, [2, True]], [False, [3]], ["4"]]
        strictly_int = is_type(int) & ~is_type(bool)
        assert list(pick(data, strictly_int)) == [2, 3]

    def test_example_built_in_predicates(self):
        data = {"id": "01353", "price": 15.42, "quantity": 68, "year": "2011"}
        numeric_strings = pick(data, NUM_STR)
        assert list(numeric_strings) == ["01353", "2011"]

    def test_example_values_for_key(self):
        data = {
            "node_id": 4,
            "child_nodes": [
                {
                    "node_id": 8,
                    "child_nodes": [
                        {
                            "node_id": 16,
                        },
                    ],
                },
                {
                    "id": 9,
                },
            ],
        }
        assert list(values_for_key(data, key="node_id")) == [4, 8, 16]
        assert list(values_for_key(data, key=["node_id", "id"])) == [4, 8, 16, 9]

    def test_example_max_depth(self):
        assert max_depth([0, [1, [2]]]) == 2
        assert max_depth({0: {1: {2: {3: {4: 4}}}}}) == 4
        assert max_depth([0, [1, []]]) == 2

    def test_example_flattening(self):
        data = [[], [0], [[[], 1], [2, [3, [4]], []], [5]]]
        assert list(pick(data, collections=False)) == [0, 1, 2, 3, 4, 5]
