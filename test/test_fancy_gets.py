"""
Test attribute lookups of different kinds
e.g. getting dict attributes, or applying functions, or getting properties from namedtuples
"""

from hashbox import HashBox
from hashbox.constants import SIZE_THRESH
import pytest


def make_dict_data():
    dicts = [
        {"t0": 0.1, "t1": 0.2, "s": "ABC"},
        {"t0": 0.3, "t1": 0.4, "s": "DEF"},
        {"t0": 0.5, "t1": 0.6, "s": "GHI"},
    ]
    return dicts


def test_dicts(index_type):
    dicts = make_dict_data()
    f = index_type(dicts, ["t0", "t1", "s"])
    result = f.find(match={"t0": [0.1, 0.3], "s": ["ABC", "DEF"]}, exclude={"t1": 0.4})
    assert result == [dicts[0]]


def test_getter_fn(index_type):
    def _middle_letter(obj):
        return obj["s"][1]

    dicts = make_dict_data()
    f = index_type(dicts, on=[_middle_letter])
    result = f.find({_middle_letter: "H"})
    assert result == [dicts[2]]


@pytest.mark.parametrize("n", [SIZE_THRESH + 1, 5])
def test_get_all(index_type, n):
    """There's a special fast-path when all items are being retrieved."""
    f = index_type([{"a": 1} for _ in range(n)], ["a"])
    result = f.find()
    assert len(result) == n
