import pytest

from hashindex.constants import SIZE_THRESH
from .conftest import BadHash, TwoHash
from hashindex import HashIndex


@pytest.mark.parametrize("n_items", [5])
def test_hash_bucket_collision(index_type, n_items):
    """
    Ensure the HashBuckets still work properly under hash collision.
    """
    items_1 = [{"b": BadHash(1)} for _ in range(n_items + 1)]
    items_2 = [{"b": BadHash(2)} for _ in range(n_items + 2)]
    items_3 = [{"b": BadHash(3)} for _ in range(n_items + 3)]
    hi = index_type(items_1 + items_2 + items_3, ["b"])
    found_1 = hi.find({"b": BadHash(1)})
    found_2 = hi.find({"b": BadHash(2)})
    found_3 = hi.find({"b": BadHash(3)})
    assert len(found_1) == len(items_1)
    assert len(found_2) == len(items_2)
    assert len(found_3) == len(items_3)
    assert all([o["b"] == BadHash(1) for o in found_1])
    assert all([o["b"] == BadHash(2) for o in found_2])
    assert all([o["b"] == BadHash(3) for o in found_3])


@pytest.mark.parametrize("n_items", [5, SIZE_THRESH + 1])
def test_get_missing_value(index_type, n_items):
    """
    When the value hashes to a bucket, but the bucket does not contain the value, is
    an empty result correctly retrieved?
    """
    data = [BadHash(i) for i in range(n_items)]
    hi = index_type(data, ["n"])
    assert len(hi.find({"n": -1})) == 0


@pytest.mark.parametrize("n_items", [5, SIZE_THRESH + 1])
def test_add_remove_two_hashes_uneven(n_items):
    data = [TwoHash(0) for _ in range(n_items)] + [TwoHash(1) for _ in range(5)]
    hi = HashIndex(on=["n"])
    for d in data:
        hi.add(d)
    for d in data:
        hi.remove(d)
    assert len(hi) == 0
