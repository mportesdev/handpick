import pytest

from handpick.core import _is_collection, _error, _iter_depth
from tests import SEQUENCES, SEQS_DICTS, COLLECTIONS


class TestIsCollection:
    def test_default(self):
        assert _is_collection([])
        assert not _is_collection(1)

        assert not _is_collection("")
        assert not _is_collection("a")
        assert not _is_collection("ab")

        assert not _is_collection(b"")
        assert not _is_collection(b"a")

    def test_strings_true(self):
        assert not _is_collection("", strings=True)
        assert not _is_collection("a", strings=True)
        assert _is_collection("ab", strings=True)

    def test_bytes_like_true(self):
        assert _is_collection(b"", bytes_like=True)
        assert _is_collection(b"a", bytes_like=True)


def test_error():
    assert _error(int, "42") is None
    assert type(_error(int, None)) is TypeError
    assert type(_error(int, "A")) is ValueError
    assert type(_error(int, "4.2e15")) is ValueError
    assert _error(float, "4.2e15") is None


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
def test_iter_depth(root, expected):
    assert list(_iter_depth(root)) == expected
