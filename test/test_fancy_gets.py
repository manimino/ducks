"""
Test attribute lookups of different kinds
e.g. getting dict attributes, or applying functions, or getting properties from namedtuples
"""
import pytest
from ducks.constants import SIZE_THRESH


def make_dict_data():
    dicts = [
        {"t0": 0.1, "t1": 0.2, "s": "ABC"},
        {"t0": 0.3, "t1": 0.4, "s": "DEF"},
        {"t0": 0.5, "t1": 0.6, "s": "GHI"},
    ]
    return dicts


def test_dicts(box_class):
    dicts = make_dict_data()
    f = box_class(dicts, ["t0", "t1", "s"])
    result = f[
        {"t0": {"in": [0.1, 0.3]}, "s": {"in": ["ABC", "DEF"]}, "t1": {"!=": 0.4},}
    ]
    assert result == [dicts[0]]


def test_getter_fn(box_class):
    def _middle_letter(obj):
        return obj["s"][1]

    dicts = make_dict_data()
    f = box_class(dicts, on=[_middle_letter])
    result = f[{_middle_letter: "H"}]
    assert result == [dicts[2]]


@pytest.mark.parametrize("n", [SIZE_THRESH + 1, 5])
def test_get_all(box_class, n):
    """There's a special fast-path when all items are being retrieved."""
    f = box_class([{"a": 1} for _ in range(n)], ["a"])
    result = f[{}]
    assert len(result) == n
