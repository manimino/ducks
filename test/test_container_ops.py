import pytest
from ducks import Dex
from ducks import FrozenDex
from ducks.constants import SIZE_THRESH


def test_iter_small(box_class):
    ls = [{"i": i} for i in range(5)]
    f = box_class(ls, ["i"])
    assert len(f) == len(ls)
    f_ls = list(f)
    assert len(f_ls) == len(ls)
    for item in ls:
        assert item in f_ls
    assert len(f_ls) == len(ls)


@pytest.mark.parametrize(
    "idx_order", [["i", "j"], ["j", "i"],],
)
def test_iter_large(box_class, idx_order):
    ls = [{"i": i, "j": -(i % 3)} for i in range(SIZE_THRESH * 3 + 3)]
    ls += [{"j": 16}]  # make sure there's at least one hasfbucket
    f = box_class(ls, idx_order)
    assert len(f) == len(ls)
    f_ls = list(f)
    assert len(f_ls) == len(ls)
    for item in ls:
        assert item in f_ls
    assert len(f_ls) == len(ls)


@pytest.mark.parametrize(
    "idx_order", [["i", "j"], ["j", "i"],],
)
def test_make_from(box_class, idx_order):
    """See if we can make one index type from the other type."""
    make_type = Dex if box_class == FrozenDex else FrozenDex
    ls = [{"i": i, "j": -(i % 3)} for i in range(SIZE_THRESH * 3 + 3)]
    f = box_class(ls, on=idx_order)
    other_f = make_type(f, on=idx_order)
    assert len(other_f) == len(f)


def test_box_contains(box_class):
    ls = [{"i": i} for i in range(5)]
    f = box_class(ls, ["i"])
    for item in ls:
        assert item in f


def test_box_not_contains(box_class):
    yes = {"i": 1}
    f = box_class([yes], "i")
    # test a ton of these because coverage can drop otherwise
    for i in [None, -1000, "apples", 1000, (1, 2, 3), 0.5] + list(range(100)):
        no = {"i": i}
        assert no not in f
