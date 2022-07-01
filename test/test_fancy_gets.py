"""
Test attribute lookups of different kinds
e.g. getting dict attributes, or applying functions, or getting properties from namedtuples
"""

from hashindex import HashIndex


def make_dict_data():
    dicts = [
        {
            't0': 0.1,
            't1': 0.2,
            's': 'ABC',
        },
        {
            't0': 0.3,
            't1': 0.4,
            's': 'DEF',
        },
        {
            't0': 0.5,
            't1': 0.6,
            's': 'GHI',
        }
    ]
    return dicts


def test_dicts(freeze):
    dicts = make_dict_data()
    hi = HashIndex(dicts, ['t0', 't1', 's'])
    if freeze:
        hi.freeze()
    result = hi.find(match={'t0': [0.1, 0.3], 's': ['ABC', 'DEF']}, exclude={'t1': 0.4})
    assert result == [dicts[0]]


def test_getter_fn(freeze):
    def _middle_letter(obj):
        return obj['s'][1]

    dicts = make_dict_data()
    hi = HashIndex(dicts, on=[_middle_letter])
    if freeze:
        hi.freeze()
    result = hi.find({_middle_letter: 'H'})
    assert result == [dicts[2]]
