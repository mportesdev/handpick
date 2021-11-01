from handpick import (
    pick,
    Predicate,
    is_type,
    not_type,
    IS_COLLECTION,
    values_for_key,
    max_depth,
)


class TestReadmeExamples:
    """Test examples from README."""

    def test_example_1(self):
        """Example from 'Simple predicate functions'."""

        data = [[1, "Py"], [-2, ["", 3.0]], -4]
        non_empty_strings = pick(data, lambda s: isinstance(s, str) and s)

        assert list(non_empty_strings) == ["Py"]

    def test_example_2(self):
        """Example from 'Non-callable predicates'."""

        data = [1, [1.0, [2, 1.0]], [{"1": 1}, [3]]]
        ones = pick(data, 1)

        assert list(ones) == [1, 1.0, 1.0, 1]

    def test_example_3(self):
        """Example from 'Handling dictionary keys'."""

        data = {"foo": {"name": "foo"}, "bar": {"name": "bar"}}
        default = pick(data, lambda s: "a" in s)
        keys_included = pick(data, lambda s: "a" in s, dict_keys=True)

        assert list(default) == ["bar"]
        assert list(keys_included) == ["name", "bar", "name", "bar"]

    def test_example_4(self):
        """Example from 'Combining predicates'."""

        @Predicate
        def is_int(n):
            return isinstance(n, int)

        @Predicate
        def is_even(n):
            return n % 2 == 0

        data = [[4, [5.0, 1], 3.0], [[15, []], {17: [7, [8], 0]}]]
        non_even_int = is_int & ~is_even
        odd_integers = pick(data, non_even_int)

        assert list(odd_integers) == [1, 15, 7]

    def test_example_5(self):
        """Example from 'Combining predicates with functions'."""

        @Predicate
        def is_list(obj):
            return isinstance(obj, list)

        data = [("1", [2]), {("x",): [(3, [4]), "5"]}, ["x", ["6"]], {7: ("x",)}]
        short_list = (lambda obj: len(obj) < 2) & is_list
        short_lists = pick(data, short_list)

        assert list(short_lists) == [[2], [4], ["6"]]

    def test_example_6(self):
        """Example from 'Suppressing errors'."""

        @Predicate
        def above_zero(n):
            return n > 0

        assert above_zero(1) is True
        assert above_zero("a") is False

        positive_numbers = pick([[1, "Py", -2], [None, 3.0]], above_zero)
        assert list(positive_numbers) == [1, 3.0]

    def test_example_7(self):
        """Example from 'Predicate factories'."""

        data = [[1.0, [2, True]], [False, [3]], ["4", {5, True}]]
        strictly_integers = pick(data, is_type(int) & not_type(bool))

        assert list(strictly_integers) == [2, 3, 5]

    def test_example_8(self):
        """Example from 'Built-in predicates'."""

        data = [[], [0], [["1"], b"2"]]
        only_values = pick(data, ~IS_COLLECTION)

        assert list(only_values) == [0, "1", b"2"]

        only_values = pick(data, lambda obj: True, collections=False)

        assert list(only_values) == [0, "1", b"2"]

    def test_example_9(self):
        """Examples from 'The values_for_key function'."""

        data = {
            "node_id": 4,
            "child_nodes": [
                {"node_id": 8, "child_nodes": [{"node_id": 16}]},
                {"node_id": 9},
            ],
        }
        node_ids = values_for_key(data, key="node_id")

        assert list(node_ids) == [4, 8, 16, 9]

    def test_example_10(self):
        """Examples from 'The max_depth function'."""

        nested_list = [0, [1, [2]]]
        nested_dict = {0: {1: {2: {3: {4: 4}}}}}

        assert max_depth(nested_list) == 2
        assert max_depth(nested_dict) == 4

        assert max_depth([0, [1, []]]) == 2

    def test_example_11(self):
        """Examples from 'Flattening nested data'."""

        data = [[], [0], [[[], 1], [2, [3, [4]], []], [5]]]
        flat_data = pick(data, not_type(list))

        assert list(flat_data) == [0, 1, 2, 3, 4, 5]
