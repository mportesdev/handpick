import pytest


@pytest.fixture
def custom_sequence():
    class CustomSequence:
        def __init__(self, sequence):
            self._seq = sequence

        def __len__(self):
            return len(self._seq)

        def __getitem__(self, item):
            return self._seq[item]

    return CustomSequence([0, 1, 2])


@pytest.fixture
def sample_sequences():
    """Basic sequences (tuple, list, str, bytes)."""
    return (
        [
            [
                "ab",
            ],
            b"cd",
            (b"ef",),
        ],
        (
            "3.14",
            "15",
        ),
    )


@pytest.fixture
def sample_subscriptables():
    """Sequences and dicts."""
    return (
        [
            [
                "ab",
            ],
            b"cd",
            {
                ("ef",): b"gh",
            },
        ],
        {
            "ij": "kl",
        },
        (
            "3.14",
            "15",
        ),
    )


@pytest.fixture
def sample_collections():
    """Sequences, dicts, sets."""
    return (
        [
            {
                "ab",
            },
            b"cd",
            {
                ("ef",): b"gh",
            },
        ],
        (
            frozenset({"3.14"}),
            "15",
        ),
    )
