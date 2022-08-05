from filterbox.constants import SIZE_THRESH
from filterbox import FilterBox
import pytest
from .conftest import BadHash, TwoHash, AssertRaises


@pytest.mark.parametrize("n_items", [1, 5, SIZE_THRESH + 1])
def test_get_stale_objects(box_class, n_items):
    objs = [{"z": BadHash(1)} for _ in range(n_items)]
    f = box_class(objs, ["z"])
    for o in objs:
        o["z"] = BadHash(2)
    found = f.find({"z": BadHash(1)})
    assert len(found) == n_items  # still finds by their old value
    found = f.find({"z": BadHash(2)})
    assert len(found) == 0


@pytest.mark.parametrize("n_items", [1, SIZE_THRESH * 2 + 2])
def test_remove_stale_objects_one_hash(n_items):
    objs = [{"z": BadHash(0)} for _ in range(n_items)]
    f = FilterBox(objs, ["z"])
    for o in objs:
        o["z"] = BadHash(1)
    with AssertRaises(KeyError):
        f.remove(objs[0])


@pytest.mark.parametrize("n_items", [1, 5, SIZE_THRESH * 2 + 2])
def test_remove_missing_object(n_items):
    objs = [{"z": TwoHash(1)} for _ in range(n_items)]
    f = FilterBox(objs, ["z"])
    with AssertRaises(KeyError):
        f.remove(TwoHash(2))


def test_external_object_modification(box_class):
    """
    What happens if the values are mutable, and someone mutates them externally?
    Answer: It screws everything up.
    But it *also* screws up Python's own set and frozenset containers, so... I think we don't need
    to go all the way into doing deepcopy() on every object we store. "Consenting adults", etc.
    At some point it's up to the user not to do weird stuff.
    """
    objs = [{'a': BadHash(1)}]
    fb = box_class(objs, 'a')
    assert len(fb.find({'a': BadHash(1)})) == 1
    objs[0]['a'].n = 5000
    # external modification changed our results
    assert len(fb.find({'a': BadHash(1)})) == 0
