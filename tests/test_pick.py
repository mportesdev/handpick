import pytest

from handpick import pick, Predicate


class TestCollectionHandling:
    def test_collections_included_by_default(self, sample_sequences):
        picked = list(pick(sample_sequences))
        assert picked == [
            [["ab"], b"cd", (b"ef",)],
            ["ab"],
            "ab",
            b"cd",
            (b"ef",),
            b"ef",
            ("3.14", "15"),
            "3.14",
            "15",
        ]

    def test_collections_excluded_optionally(self, sample_sequences):
        picked = list(pick(sample_sequences, collections=False))
        assert picked == ["ab", b"cd", b"ef", "3.14", "15"]

    def test_collections_in_dict_keys_included_by_default(self, sample_subscriptables):
        picked = list(pick(sample_subscriptables, dict_keys=True))
        assert picked == [
            [["ab"], b"cd", {("ef",): b"gh"}],
            ["ab"],
            "ab",
            b"cd",
            {("ef",): b"gh"},
            ("ef",),
            "ef",
            b"gh",
            {"ij": "kl"},
            "ij",
            "kl",
            ("3.14", "15"),
            "3.14",
            "15",
        ]

    def test_collections_in_dict_keys_excluded_optionally(self, sample_subscriptables):
        picked = list(pick(sample_subscriptables, collections=False, dict_keys=True))
        assert picked == ["ab", b"cd", "ef", b"gh", "ij", "kl", "3.14", "15"]


class TestFunctionsAndPredicates:
    def test_simple_function(self, sample_collections):
        picked = list(pick(sample_collections, lambda s: hasattr(s, "count")))
        assert picked == [
            [{"ab"}, b"cd", {("ef",): b"gh"}],
            "ab",
            b"cd",
            b"gh",
            (frozenset({"3.14"}), "15"),
            "3.14",
            "15",
        ]

    def test_function_raises_error(self, sample_collections):
        with pytest.raises(TypeError):
            list(pick(sample_collections, lambda s: s[1]))

    def test_predicate_suppresses_errors(self, sample_collections):
        picked = list(pick(sample_collections, Predicate(lambda s: s[1])))
        assert picked == [
            [{"ab"}, b"cd", {("ef",): b"gh"}],
            "ab",
            b"cd",
            b"gh",
            (frozenset({"3.14"}), "15"),
            "3.14",
            "15",
        ]


class TestDictKeyHandling:
    def test_dict_keys_excluded_by_default(self, sample_subscriptables):
        picked = list(pick(sample_subscriptables, lambda t: isinstance(t, tuple)))
        assert picked == [("3.14", "15")]

    def test_dict_keys_included_optionally(self, sample_subscriptables):
        picked = list(
            pick(sample_subscriptables, lambda t: isinstance(t, tuple), dict_keys=True)
        )
        assert picked == [("ef",), ("3.14", "15")]


class TestSpecialCases:
    def test_empty_root_yields_nothing(self):
        assert list(pick([])) == []

    def test_non_iterable_root_yields_nothing(self):
        assert list(pick(None)) == []

    def test_non_callable_predicate_raises_error(self, sample_collections):
        with pytest.raises(TypeError, match="predicate must be callable"):
            list(pick(sample_collections, 42))

    def test_omitted_predicate_yields_everything(self):
        assert list(pick([{1: 2}])) == [{1: 2}, 2]
        assert list(pick([{1: 2}], collections=False)) == [2]
        assert list(pick([{1: 2}], dict_keys=True)) == [{1: 2}, 1, 2]

    def test_custom_sequence(self, custom_sequence):
        assert list(pick(custom_sequence, bool)) == [1, 2]

    def test_custom_sequence_no_predicate(self, custom_sequence):
        assert list(pick(custom_sequence)) == [0, 1, 2]


class TestStringsAndBytesLike:
    @pytest.mark.parametrize(
        "data, expected",
        (
            pytest.param(["hand"], ["hand"], id="string len > 1"),
            pytest.param(["a"], ["a"], id="string len 1"),
            pytest.param(["ab", ["cd"]], ["ab", "cd"], id="nested"),
            pytest.param("pick", [], id="top-level string len > 1"),
            pytest.param("a", [], id="top-level string len 1"),
        ),
    )
    def test_strings_not_iterated_by_default(self, data, expected):
        assert list(pick(data, lambda s: isinstance(s, str))) == expected

    @pytest.mark.parametrize(
        "data, expected",
        (
            pytest.param(["hand"], ["hand", "h", "a", "n", "d"], id="string len > 1"),
            pytest.param(["a"], ["a"], id="string len 1"),
            pytest.param([""], [""], id="empty string"),
            pytest.param(["ab", ["cd"]], ["ab", "a", "b", "cd", "c", "d"], id="nested"),
            pytest.param("pick", ["p", "i", "c", "k"], id="top-level string len > 1"),
            pytest.param("a", [], id="top-level string len 1"),
            pytest.param("", [], id="top-level empty string"),
        ),
    )
    def test_strings_iterated_optionally(self, data, expected):
        assert list(pick(data, lambda s: isinstance(s, str), strings=True)) == expected

    def test_strings_not_picked_but_iterated_optionally(self):
        data = ["foo", 42, b"bar"]
        picked = list(pick(data, collections=False, strings=True))
        assert picked == ["f", "o", "o", 42, b"bar"]

    @pytest.mark.parametrize(
        "data, expected",
        (
            pytest.param([b"hand"], [b"hand"], id="bytes"),
            pytest.param([[b"PY"], b"12"], [[b"PY"], b"PY", b"12"], id="nested"),
            pytest.param(bytearray([4, 2]), [], id="top-level bytes"),
        ),
    )
    def test_bytes_like_not_iterated_by_default(self, data, expected):
        assert list(pick(data)) == expected

    @pytest.mark.parametrize(
        "data, expected",
        (
            pytest.param(
                [b"hand"], [b"hand", ord("h"), ord("a"), ord("n"), ord("d")], id="bytes"
            ),
            pytest.param(
                [[b"P"], b"Y"], [[b"P"], b"P", ord("P"), b"Y", ord("Y")], id="nested"
            ),
            pytest.param(bytearray([4, 2]), [4, 2], id="top-level bytes"),
        ),
    )
    def test_bytes_like_iterated_optionally(self, data, expected):
        assert list(pick(data, bytes_like=True)) == expected

    def test_bytes_like_not_picked_but_iterated_optionally(self):
        data = ["foo", 42, b"bar"]
        picked = list(pick(data, collections=False, bytes_like=True))
        assert picked == ["foo", 42, ord("b"), ord("a"), ord("r")]
