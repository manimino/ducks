import pytest

from ducks.constants import SIZE_THRESH
from ducks import Dex
from .conftest import Attr, AssertRaises


@pytest.mark.parametrize("n_items", [5, SIZE_THRESH + 1])
def test_get_stale_objects(box_class, n_items):
    objs = [{"z": Attr(1)} for _ in range(n_items)]
    f = box_class(objs, ["z"])
    for o in objs:
        o["z"] = Attr(2)
    found = f[{"z": Attr(1)}]
    assert len(found) == n_items  # still finds by their old value
    found = f[{"z": Attr(2)}]
    assert len(found) == 0


@pytest.mark.parametrize("n_items", [1, SIZE_THRESH * 2 + 2])
def test_remove_stale_objects(n_items):
    objs = [{"z": 1} for _ in range(n_items)]
    f = Dex(objs, ["z"])
    for o in objs:
        o["z"] = 2
    for o in objs:
        f.remove(o)
    assert len(f) == 0
    assert len(f._indexes["z"]) == 0


@pytest.mark.parametrize("n_items", [1, 5, SIZE_THRESH * 2 + 2])
def test_remove_missing_object(n_items):
    objs = [{"z": Attr(1)} for _ in range(n_items)]
    f = Dex(objs, ["z"])
    with AssertRaises(KeyError):
        f.remove(Attr(2))


def test_external_object_modification(box_class):
    """
    What happens if the values are mutable, and someone mutates them externally?
    Answer: It gives an unexpected result. Attributes are stored by reference, so
    if the attribute is mutated externally, it will change inside the container as well.
    Luckily, this is rare; most attributes will be ints and strings which are immutable.
    Other python containers have the same problem -- you can break a frozenset if it has
    a mutable attribute as a key, for example.
    """
    objs = [{"a": Attr(1)}]
    fb = box_class(objs, "a")
    assert len(fb[{"a": Attr(1)}]) == 1
    objs[0]["a"].n = 5000
    # external modification changed our results
    assert len(fb[{"a": Attr(1)}]) == 0
    assert len(fb[{"a": Attr(5000)}]) == 1
