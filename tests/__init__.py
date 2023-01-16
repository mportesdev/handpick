def is_even(n):
    return n % 2 == 0


def is_positive(n):
    return n > 0


def first_item_positive(collection):
    return collection[0] > 0


def palindromic_int(n):
    return int(str(n)[::-1]) == n


# basic sequences (tuple, list, str, bytes, bytearray)

SEQUENCES = (
    [
        [
            "hand",
        ],
        b"pick",
        (
            42,
            b"hand",
        ),
    ],
    (
        "3.14",
        (1.414,),
        [
            "15",
            bytearray(b"pick"),
        ],
    ),
)


# similar to above, modified to contain dictionaries

SEQS_DICTS = (
    [
        [
            "hand",
        ],
        b"pick",
        {
            42: b"hand",
        },
    ],
    (
        "3.14",
        (1.414,),
        {
            ("15",): bytearray(b"pick"),
        },
    ),
)


# similar to above, modified to contain set and frozenset

COLLECTIONS = (
    [
        {
            "hand",
        },
        b"pick",
        {
            42: b"hand",
        },
    ],
    (
        "3.14",
        (frozenset({1.414}),),
        {
            ("15",): bytearray(b"pick"),
        },
    ),
)
