import pytest
from hashindex import HashIndex, FrozenHashIndex
from hashindex.constants import SIZE_THRESH


def test_iter_small(index_type):
    ls = [{"i": i} for i in range(5)]
    hi = index_type(ls, ["i"])
    assert len(hi) == len(ls)
    hi_ls = list(hi)
    assert len(hi_ls) == len(ls)
    for item in ls:
        assert item in hi_ls
    assert len(hi_ls) == len(ls)


@pytest.mark.parametrize("idx_order", [["i", "j"], ["j", "i"],])
def test_iter_large(index_type, idx_order):
    ls = [{"i": i, "j": -(i % 3)} for i in range(SIZE_THRESH * 3 + 3)]
    ls += [{"j": 16}]  # make sure there's at least one hashbucket
    hi = index_type(ls, idx_order)
    assert len(hi) == len(ls)
    hi_ls = list(hi)
    assert len(hi_ls) == len(ls)
    for item in ls:
        assert item in hi_ls
    assert len(hi_ls) == len(ls)


@pytest.mark.parametrize("idx_order", [["i", "j"], ["j", "i"],])
def test_make_from(index_type, idx_order):
    """See if we can make one index type from the other type."""
    make_type = HashIndex if index_type == FrozenHashIndex else FrozenHashIndex
    ls = [{"i": i, "j": -(i % 3)} for i in range(SIZE_THRESH * 3 + 3)]
    hi = index_type(ls, on=idx_order)
    other_hi = make_type(hi, on=idx_order)
    assert len(other_hi) == len(hi)


def test_contains(index_type):
    ls = [{"i": i} for i in range(5)]
    hi = index_type(ls, ["i"])
    for item in ls:
        assert item in hi
