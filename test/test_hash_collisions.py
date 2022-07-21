import pytest

from hashindex.constants import SIZE_THRESH
from .conftest import BadHash, TwoHash
from hashindex import HashIndex

def test_dict_bucket_collision(index_type):
    """
    Ensure the DictBuckets still work properly under hash collision.
    """
    items_1 = [BadHash(1) for _ in range(SIZE_THRESH+1)]
    items_2 = [BadHash(2) for _ in range(SIZE_THRESH+2)]
    hi = index_type(items_1+items_2, ['n'])
    found_1 = hi.find({'n': 1})
    found_2 = hi.find({'n': 2})
    assert len(found_1) == len(items_1)
    assert len(found_2) == len(items_2)
    assert all([o.n == 1 for o in found_1])
    assert all([o.n == 2 for o in found_2])


def test_hash_bucket_collision(index_type):
    """
    Ensure the HashBuckets still work properly under hash collision.
    """
    items_1 = [BadHash(1) for _ in range(5)]
    items_2 = [BadHash(2) for _ in range(6)]
    hi = index_type(items_1+items_2, ['n'])
    found_1 = hi.find({'n': 1})
    found_2 = hi.find({'n': 2})
    assert len(found_1) == len(items_1)
    assert len(found_2) == len(items_2)
    assert all([o.n == 1 for o in found_1])
    assert all([o.n == 2 for o in found_2])


@pytest.mark.parametrize('n_items', [5, SIZE_THRESH+1])
def test_get_missing_value(index_type, n_items):
    """
    When the value hashes to a bucket, but the bucket does not contain the value, is
    an empty result correctly retrieved?
    """
    data = [BadHash(i) for i in range(n_items)]
    hi = index_type(data, ['n'])
    assert len(hi.find({'n': -1})) == 0


@pytest.mark.parametrize('n_items', [5, SIZE_THRESH+1])
def test_add_remove_two_hashes_uneven(n_items):
    data = [TwoHash(0) for _ in range(n_items)] + [TwoHash(1) for _ in range(5)]
    hi = HashIndex(on=['n'])
    for d in data:
        hi.add(d)
    for d in data:
        hi.remove(d)
    assert len(hi) == 0
