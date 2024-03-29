import pytest
from ducks.constants import ARRAY_SIZE_MAX
from ducks.constants import SET_SIZE_MIN
from ducks.constants import SIZE_THRESH


@pytest.mark.parametrize(
    "n_items", [SIZE_THRESH, ARRAY_SIZE_MAX + 1, SET_SIZE_MIN - 1, SET_SIZE_MIN + 1]
)
def test_many_gets(box_class, n_items):
    """At one point there was a bug involving several sequential gets, let's make sure that can't come back."""

    def f5(i):
        return i["n"] % 5

    data = [{"n": i} for i in range(n_items)]
    f = box_class(data, ["n", f5])
    for _ in range(4):
        # just a lot of queries in every conceivable flavor
        assert len(f[{"n": {"in": [1, 2, 3, 4, 5]}, f5: {"in": [3, 4]}}]) == 2
        assert len(f[{"n": {"in": [1, 2]}, f5: {"in": [1, 2]}}]) == 2
        assert len(f[{"n": {"in": [1, 2, 3, 4, 5]}}]) == 5
        assert len(f[{"n": {"in": [1, 2, 3, 4, 5]}, f5: {"not in": [1, 2]}}]) == 3
        assert len(f[{"n": {"in": [6, 7, 8], "!=": 3}, f5: {"not in": [1, 2]}}]) == 1
        assert (
            len(f[{"n": {"in": [6, 7, 8], "!=": -1000}, f5: {"not in": [3, 4]}}]) == 2
        )
        assert (
            len(f[{f5: {"==": 1, "in": [3, 4]}, "n": {"==": -1000, "!=": -1000}}]) == 0
        )
        assert (
            len(
                f[
                    {
                        "n": {"in": [-1000, 3, 4, 5], "!=": -1000},
                        f5: {"not in": [3, 4]},
                    }
                ]
            )
            == 1
        )
        assert len(f[{}]) == n_items


def test_mutated_return(box_class):
    """If the user modifies the returned array, none of our arrays change, right?"""
    data = [{"n": 0} for _ in range(5)]
    f = box_class(data, ["n"])
    arr = f[{"n": 0}]
    assert len(arr) == 5
    assert all(a["n"] == 0 for a in arr)
    arr[0] = {"n": 1}
    arr2 = f[{"n": 0}]
    assert len(arr) == 5
    assert all(a["n"] == 0 for a in arr2)
