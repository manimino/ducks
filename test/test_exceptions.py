import pytest

from filterbox import FilterBox, FrozenFilterBox, ConcurrentFilterBox
from filterbox.exceptions import AttributeNotFoundError
from filterbox.constants import SIZE_THRESH

from .conftest import AssertRaises, BadHash


def test_remove_empty():
    f = FilterBox([], on=["stuff"])
    with AssertRaises(KeyError):
        f.remove("nope")


def test_empty_frozen():
    with AssertRaises(ValueError):
        FrozenFilterBox([], on=["stuff"])


def test_no_index():
    with AssertRaises(ValueError):
        FilterBox(["a"])


def test_empty_index():
    with AssertRaises(ValueError):
        FrozenFilterBox(["a"], [])


def test_bad_query(box_class):
    f = box_class([{"a": 1}], on=["a"])
    with AssertRaises(TypeError):
        f.find(match=[])
    with AssertRaises(TypeError):
        f.find(["a", 1])
    with AssertRaises(AttributeNotFoundError):
        f.find({"b": 1})


@pytest.mark.parametrize("n_items", [1, 5, SIZE_THRESH + 1])
def test_remove_missing_value(n_items):
    """
    When the value hashes to a bucket, but the bucket does not contain the value, is
    an empty result correctly retrieved?
    """
    data = [BadHash(i) for i in range(5)]
    f = FilterBox(data, ["n"])
    assert len(f.find({"n": -1})) == 0
    with AssertRaises(KeyError):
        f.remove(BadHash(-1))


def test_bad_priority():
    with AssertRaises(ValueError):
        _ = ConcurrentFilterBox(None, on=['x'], priority='lol')
