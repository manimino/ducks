import numpy as np
import pytest

from filtered.constants import SIZE_THRESH

"""
@pytest.mark.parametrize(
    "counts, result",
    [
        ([1, 1, 1000, 1, 1], np.array([0, 2, 3])),
        ([55, 55, 55, 55], np.array([0, 1, 2, 3])),
        ([1000, 1, 1, 1000], np.array([0, 1, 3])),
    ],
)
def test_find_bucket_starts(counts, result):
    assert all(find_bucket_starts(counts, 100) == result)


def test_compute_buckets():
    objs = list({"a": i} for i in range(1000))
    bucket_plans = compute_buckets(objs, "a", SIZE_THRESH)
    bucket_objs = []
    for b in bucket_plans:
        for o in b.obj_arr:
            bucket_objs.append(o)
    assert len(bucket_objs) == len(objs)


def test_compute_buckets_mini():
    # uses the fact that hash() on a small positive integer is just the integer
    objs = [{"a": int(i / 2)} for i in range(20)]
    for limit in [1, 2]:  # limit 1 makes ten DictBuckets, 2 makes ten HashBuckets
        bucket_plans = compute_buckets(objs, "a", limit)
        assert len(bucket_plans) == 10
        for i, b in enumerate(bucket_plans):
            assert i in b.val_arr
            assert len(b.val_arr) == 2
"""
