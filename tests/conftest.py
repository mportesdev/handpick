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
