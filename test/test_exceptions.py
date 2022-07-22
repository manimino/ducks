from hashindex import HashIndex, FrozenHashIndex
from hashindex.exceptions import MissingObjectError, MissingIndexError
from hashindex.constants import SIZE_THRESH
import pytest

from .conftest import AssertRaises, BadHash


def test_remove_empty():
    hi = HashIndex([], on=["stuff"])
    with AssertRaises(MissingObjectError):
        hi.remove("nope")


def test_empty_frozen():
    with AssertRaises(ValueError):
        FrozenHashIndex([], on=["stuff"])


def test_no_index_mutable(index_type):
    with AssertRaises(ValueError):
        index_type(["a"])


def test_bad_query(index_type):
    hi = index_type([0], on=["a"])
    with AssertRaises(TypeError):
        hi.find(match=[])
    with AssertRaises(TypeError):
        hi.find(["a", 1])
    with AssertRaises(MissingIndexError):
        hi.find({"b": 1})


@pytest.mark.parametrize("n_items", [5, SIZE_THRESH + 1])
def test_remove_missing_value(n_items):
    """
    When the value hashes to a bucket, but the bucket does not contain the value, is
    an empty result correctly retrieved?
    """
    data = [BadHash(i) for i in range(5)]
    hi = HashIndex(data, ["n"])
    assert len(hi.find({"n": -1})) == 0
    with AssertRaises(MissingObjectError):
        hi.remove(BadHash(-1))

