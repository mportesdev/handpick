import pytest

from handpick import pick, Predicate

from tests import SEQUENCES, COLLECTIONS, SEQS_DICTS


class TestCollectionHandling:
    def test_collections_included_by_default(self):
        picked = list(pick(SEQUENCES, lambda x: True))
        assert picked == [
            [["hand"], b"pick", (42, b"hand")],
            ["hand"],
            "hand",
            b"pick",
            (42, b"hand"),
            42,
            b"hand",
            ("3.14", (1.414,), ["15", bytearray(b"pick")]),
            "3.14",
            (1.414,),
            1.414,
            ["15", bytearray(b"pick")],
            "15",
            bytearray(b"pick"),
        ]

    def test_collections_excluded_optionally(self):
        picked = list(pick(SEQUENCES, lambda x: True, collections=False))
        assert picked == [
            "hand",
            b"pick",
            42,
            b"hand",
            "3.14",
            1.414,
            "15",
            bytearray(b"pick"),
        ]

    def test_collections_in_dict_keys_included_by_default(self):
        picked = list(pick(SEQS_DICTS, lambda x: True, dict_keys=True))
        assert picked == [
            [["hand"], b"pick", {42: b"hand"}],
            ["hand"],
            "hand",
            b"pick",
            {42: b"hand"},
            42,
            b"hand",
            ("3.14", (1.414,), {("15",): bytearray(b"pick")}),
            "3.14",
            (1.414,),
            1.414,
            {("15",): bytearray(b"pick")},
            ("15",),
            "15",
            bytearray(b"pick"),
        ]

    def test_collections_in_dict_keys_excluded_optionally(self):
        picked = list(
            pick(SEQS_DICTS, lambda x: True, collections=False, dict_keys=True)
        )
        assert picked == [
            "hand",
            b"pick",
            42,
            b"hand",
            "3.14",
            1.414,
            "15",
            bytearray(b"pick"),
        ]


class TestFunctionsAndPredicates:
    def test_simple_function(self):
        picked = list(pick(COLLECTIONS, lambda s: hasattr(s, "count")))
        assert picked == [
            [{"hand"}, b"pick", {42: b"hand"}],
            "hand",
            b"pick",
            b"hand",
            ("3.14", (frozenset({1.414}),), {("15",): bytearray(b"pick")}),
            "3.14",
            (frozenset({1.414}),),
            bytearray(b"pick"),
        ]

    def test_function_raises_error(self):
        with pytest.raises(TypeError, match="'set' object does not support indexing"):
            list(pick(COLLECTIONS, lambda s: s[1]))

    def test_predicate_suppresses_errors(self):
        picked = list(pick(COLLECTIONS, Predicate(lambda s: s[1])))
        assert picked == [
            [{"hand"}, b"pick", {42: b"hand"}],
            "hand",
            b"pick",
            b"hand",
            ("3.14", (frozenset({1.414}),), {("15",): bytearray(b"pick")}),
            "3.14",
            bytearray(b"pick"),
        ]


class TestDictKeyHandling:
    def test_dict_keys_excluded_by_default(self):
        picked = list(pick(SEQS_DICTS, lambda t: isinstance(t, tuple)))
        assert picked == [
            ("3.14", (1.414,), {("15",): bytearray(b"pick")}),
            (1.414,),
        ]

    def test_dict_keys_included_optionally(self):
        picked = list(pick(SEQS_DICTS, lambda t: isinstance(t, tuple), dict_keys=True))
        assert picked == [
            ("3.14", (1.414,), {("15",): bytearray(b"pick")}),
            (1.414,),
            ("15",),
        ]


class TestSpecialCases:
    def test_empty_root_yields_nothing(self):
        assert list(pick([], lambda x: True)) == []

    def test_non_iterable_root_yields_nothing(self):
        assert list(pick(None, lambda x: True)) == []

    def test_non_callable_predicate(self):
        assert list(pick(COLLECTIONS, b"pick")) == [b"pick", bytearray(b"pick")]


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
            pytest.param(["ab", ["cd"]], ["ab", "a", "b", "cd", "c", "d"], id="nested"),
            pytest.param("pick", ["p", "i", "c", "k"], id="top-level string len > 1"),
            pytest.param("a", [], id="top-level string len 1"),
        ),
    )
    def test_strings_iterated_optionally(self, data, expected):
        assert list(pick(data, lambda s: isinstance(s, str), strings=True)) == expected

    @pytest.mark.parametrize(
        "data, expected",
        (
            pytest.param([b"hand"], [b"hand"], id="bytes"),
            pytest.param([[b"PY"], b"12"], [[b"PY"], b"PY", b"12"], id="nested"),
            pytest.param(bytearray([4, 2]), [], id="top-level bytes"),
        ),
    )
    def test_bytes_like_not_iterated_by_default(self, data, expected):
        assert list(pick(data, lambda x: True)) == expected

    @pytest.mark.parametrize(
        "data, expected",
        (
            pytest.param([b"hand"], [b"hand", 104, 97, 110, 100], id="bytes"),
            pytest.param([[b"P"], b"Y"], [[b"P"], b"P", 80, b"Y", 89], id="nested"),
            pytest.param(bytearray([4, 2]), [4, 2], id="top-level bytes"),
        ),
    )
    def test_bytes_like_iterated_optionally(self, data, expected):
        assert list(pick(data, lambda x: True, bytes_like=True)) == expected
