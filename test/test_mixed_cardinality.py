import pytest

from filterbox.constants import SIZE_THRESH
from .conftest import BadHash


@pytest.mark.parametrize("thresh", [10 ** i for i in range(5)])
def test_thresh(box_class, thresh):
    def size_thresh_n(obj):
        return obj["size"] < thresh

    n_items = 10 ** 4
    objs = [{"size": i} for i in range(n_items)]
    fb = box_class(objs, [size_thresh_n])
    assert len(fb.find({size_thresh_n: True})) == thresh
    assert len(fb.find({size_thresh_n: False})) == n_items - thresh


def test_bad_hash_mixed(box_class):
    objs = [{"n": BadHash(i)} for i in range(100)] + [{"n": BadHash(0)} for _ in range(SIZE_THRESH+1)]
    fb = box_class(objs, ['n'])
    assert len(fb.find({'n': objs[1]['n']})) == 1
    assert len(fb.find({'n': objs[0]['n']})) == SIZE_THRESH+2
