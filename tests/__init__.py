import json
from pathlib import Path

TEST_DATA_PATH = Path(__file__).parent / 'data'


def from_json(filename):
    with open(TEST_DATA_PATH / filename) as f:
        data = json.load(f)
    return data


def is_int(obj):
    return isinstance(obj, int)


FLAT = (62, 0.0, True, 'food', '', None, [], 'foo', {})

NESTED_LIST = [
    [1, 2, 100.0],
    [3, 'Py', [{}, 4], 5],
]

DICT_LIST = {
    1: [
        {},
        (2, '3'),
    ],
    4: [
        {},
        [5, ()],
    ],
}

LIST_TUPLE = [
    [
        None,
        (
            (1, 2, 3),
            3,
        ),
        0,
    ],
    ('foo', 'bar'),
]

NESTED_DICT = {
    '1': {
        'dict': {
            'list': [],
            'tuple': (),
        },
        'list': [1, [2, [3, {}]]],
    },
    '2': {
        'dict': {
            'list': [],
            'tuple': (),
        },
        'tuple': ({}, [], ()),
    },
}

LIST_5_LEVELS = [
    [
        [
            bytearray(b'2'),
            [
                ['4'],
                3.5,
            ],
        ],
        b'1',
    ],
    '0',
    [
        [
            '2',
            [b'3'],
        ],
        '1',
        (2,),
    ],
]

DICT_5_LEVELS = {
    '0_key1': '0_value1',
    '0_key2': {
        '1_key1': {
            '2_key1': '2_value1',
            '2_key2': {
                '3_key1': {'4_key': '4_value'},
                '3_key2': {'4_value2'}
            },
        },
        '1_key2': '1_value2',
    },
}
