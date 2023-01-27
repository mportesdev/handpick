import pytest

from handpick.core import _is_collection, _is_mapping, _error, _iter_depth


class TestIsCollection:
    def test_default(self):
        assert _is_collection([])
        assert not _is_collection(1)
        assert not _is_collection("")

        assert not _is_collection(b"")
        assert not _is_collection(b"a")

    def test_bytes_like_true(self):
        assert _is_collection(b"", bytes_like=True)
        assert _is_collection(b"a", bytes_like=True)

    def test_custom_sequence(self, custom_sequence):
        assert _is_collection(custom_sequence)


def test_is_mapping():
    assert _is_mapping({})
    assert not _is_mapping(42)
    assert not _is_mapping([])


def test_error():
    assert _error(int, "42") is None
    assert type(_error(int, None)) is TypeError
    assert type(_error(int, "A")) is ValueError
    assert type(_error(int, "4.2e15")) is ValueError
    assert _error(float, "4.2e15") is None


@pytest.mark.parametrize(
    "root, expected",
    (
        pytest.param(
            ([["ab"], b"cd", (b"ef",)], ("3.14", "15")),
            [0, 1, 2, 2, 1],
            id="sequences",
        ),
        pytest.param(
            ([["ab"], b"cd", {("ef",): b"gh"}], {"ij": "kl"}, ("3.14", "15")),
            [0, 1, 2, 2, 1, 1],
            id="sequences+dicts",
        ),
        pytest.param(
            ([{"ab"}, b"cd", {("ef",): b"gh"}], (frozenset({"3.14"}), "15")),
            [0, 1, 2, 2, 1, 2],
            id="collections",
        ),
        pytest.param([], [0], id="[]"),
        pytest.param([[]], [0, 1], id="[[]]"),
    ),
)
def test_iter_depth(root, expected):
    assert list(_iter_depth(root)) == expected
