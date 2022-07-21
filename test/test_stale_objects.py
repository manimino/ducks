from hashindex.constants import SIZE_THRESH
from hashindex import HashIndex
import pytest
from .conftest import BadHash, TwoHash, AssertRaises
from hashindex.exceptions import StaleObjectRemovalError, MissingObjectError



@pytest.mark.parametrize('n_items', [5, SIZE_THRESH+1])
def test_get_stale_objects(index_type, n_items):
    objs = [{'z': BadHash(1)} for _ in range(n_items)]
    hi = index_type(objs, ['z'])
    for o in objs:
        o['z'] = BadHash(2)  # updated without calling update()
    found = hi.find({'z': BadHash(1)})
    assert len(found) == 0
    found = hi.find({'z': BadHash(2)})
    assert len(found) == 0


@pytest.mark.parametrize('n_items', [SIZE_THRESH*2+2])
def test_remove_stale_objects_one_hash(n_items):
    objs = [{'z': BadHash(0)} for _ in range(n_items)]
    hi = HashIndex(objs, ['z'])
    for o in objs:
        o['z'] = BadHash(1)  # updated without calling update()
    with AssertRaises(StaleObjectRemovalError):
        hi.remove(objs[0])


@pytest.mark.parametrize('n_items', [5, SIZE_THRESH*2+2])
def test_remove_stale_objects_two_hash(n_items):
    objs = [{'z': TwoHash(0)} for _ in range(n_items)]
    hi = HashIndex(objs, ['z'])
    for o in objs:
        o['z'] = TwoHash(1)  # updated without calling update()
    with AssertRaises(StaleObjectRemovalError):
        hi.remove(objs[0])


@pytest.mark.parametrize('n_items', [5, SIZE_THRESH*2+2])
def test_remove_missing_object(n_items):
    objs = [{'z': TwoHash(1)} for _ in range(n_items)]
    hi = HashIndex(objs, ['z'])
    with AssertRaises(MissingObjectError):
        hi.remove(TwoHash(2))
