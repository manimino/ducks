import pytest
from ducks import ConcurrentDex
from ducks import Dex
from ducks import FrozenDex
from ducks.constants import SIZE_THRESH
from ducks.exceptions import AttributeNotFoundError

from .conftest import AssertRaises
from .conftest import Attr


def test_remove_empty():
    f = Dex([], on=["stuff"])
    with AssertRaises(KeyError):
        f.remove("nope")


def test_no_index():
    with AssertRaises(ValueError):
        Dex(["a"])


def test_empty_index():
    with AssertRaises(ValueError):
        FrozenDex(["a"], [])


def test_bad_query(box_class):
    f = box_class([{"a": 1}], on=["a"])
    with AssertRaises(TypeError):
        _ = f[[]]
    with AssertRaises(TypeError):
        _ = f[["a", 1]]
    with AssertRaises(AttributeNotFoundError):
        _ = f[{"b": 1}]


@pytest.mark.parametrize("n_items", [1, 5, SIZE_THRESH + 1])
def test_remove_missing_value(n_items):
    """
    When the value hashes to a bucket, but the bucket does not contain the value, is
    an empty result correctly retrieved?
    """
    data = [Attr(i) for i in range(5)]
    f = Dex(data, ["n"])
    assert len(f[{"n": -1}]) == 0
    with AssertRaises(KeyError):
        f.remove(Attr(-1))


def test_bad_priority():
    with AssertRaises(ValueError):
        _ = ConcurrentDex(None, on=["x"], priority="lol")


def test_bad_expr(box_class):
    f = box_class(["ok"], on="x")
    with AssertRaises(ValueError):
        _ = f[{"x": {">", 2}}]


def test_bad_operator(box_class):
    f = box_class(["ok"], on="x")
    with AssertRaises(ValueError):
        _ = f[{"x": {"qq": 2}}]


def test_bad_gt_lt(box_class):
    f = box_class(["ok"], on="x")
    with AssertRaises(ValueError):
        _ = f[{"x": {">": 2, ">=": 3}}]
    with AssertRaises(ValueError):
        _ = f[{"x": {"<": 2, "<=": 3}}]
