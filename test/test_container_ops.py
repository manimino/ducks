import pytest
from hashbox import HashBox, FrozenHashBox
from hashbox.constants import SIZE_THRESH


def test_iter_small(box_class):
    ls = [{"i": i} for i in range(5)]
    f = box_class(ls, ["i"])
    assert len(f) == len(ls)
    f_ls = list(f)
    assert len(f_ls) == len(ls)
    for item in ls:
        assert item in f_ls
    assert len(f_ls) == len(ls)


@pytest.mark.parametrize("idx_order", [["i", "j"], ["j", "i"],])
def test_iter_large(box_class, idx_order):
    ls = [{"i": i, "j": -(i % 3)} for i in range(SIZE_THRESH * 3 + 3)]
    ls += [{"j": 16}]  # make sure there's at least one hashbucket
    f = box_class(ls, idx_order)
    assert len(f) == len(ls)
    f_ls = list(f)
    assert len(f_ls) == len(ls)
    for item in ls:
        assert item in f_ls
    assert len(f_ls) == len(ls)


@pytest.mark.parametrize("idx_order", [["i", "j"], ["j", "i"],])
def test_make_from(box_class, idx_order):
    """See if we can make one index type from the other type."""
    make_type = HashBox if box_class == FrozenHashBox else FrozenHashBox
    ls = [{"i": i, "j": -(i % 3)} for i in range(SIZE_THRESH * 3 + 3)]
    f = box_class(ls, on=idx_order)
    other_f = make_type(f, on=idx_order)
    assert len(other_f) == len(f)


def test_contains(box_class):
    ls = [{"i": i} for i in range(5)]
    f = box_class(ls, ["i"])
    for item in ls:
        assert item in f


def test_not_contains(box_class):
    yes = {"i": 1}
    f = box_class([yes], "i")
    no = {"i": -1000}
    assert no not in f
