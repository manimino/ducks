import numpy as np
import pytest

from hashindex.constants import SIZE_THRESH
from hashindex.init_helpers import compute_buckets, find_bucket_starts


@pytest.mark.parametrize("counts, result", [
    ([1, 1, 1000, 1, 1], np.array([0, 2, 3])),
    ([55, 55, 55, 55], np.array([0, 1, 2, 3])),
    ([1000, 1, 1, 1000], np.array([0, 1, 3]))
])
def test_find_bucket_starts(counts, result):
    assert all(find_bucket_starts(counts, 100) == result)


def test_compute_buckets():
    objs = list({'a': i} for i in range(1000))
    bucket_plans = compute_buckets(objs, 'a', SIZE_THRESH)
    bucket_objs = []
    for b in bucket_plans:
        for o in b.obj_arr:
            bucket_objs.append(o)
    assert len(bucket_objs) == len(objs)
