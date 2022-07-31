from hashbox.constants import SIZE_THRESH
from hashbox import HashBox
import pytest
from .conftest import BadHash, TwoHash, AssertRaises


@pytest.mark.parametrize("n_items", [5, SIZE_THRESH + 1])
def test_get_stale_objects(box_class, n_items):
    objs = [{"z": BadHash(1)} for _ in range(n_items)]
    f = box_class(objs, ["z"])
    for o in objs:
        o["z"] = BadHash(2)
    found = f.find({"z": BadHash(1)})
    assert len(found) == n_items  # still finds by their old value
    found = f.find({"z": BadHash(2)})
    assert len(found) == 0


@pytest.mark.parametrize("n_items", [SIZE_THRESH * 2 + 2])
def test_remove_stale_objects_one_hash(n_items):
    objs = [{"z": BadHash(0)} for _ in range(n_items)]
    f = HashBox(objs, ["z"])
    for o in objs:
        o["z"] = BadHash(1)
    with AssertRaises(KeyError):
        f.remove(objs[0])


@pytest.mark.parametrize("n_items", [5, SIZE_THRESH * 2 + 2])
def test_remove_missing_object(n_items):
    objs = [{"z": TwoHash(1)} for _ in range(n_items)]
    f = HashBox(objs, ["z"])
    with AssertRaises(KeyError):
        f.remove(TwoHash(2))
