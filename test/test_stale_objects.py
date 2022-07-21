from hashindex.constants import SIZE_THRESH
from hashindex import HashIndex
import pytest
from .conftest import BadHash


@pytest.mark.parametrize('n_items', [5, SIZE_THRESH+1])
def test_get_stale_objects(index_type, n_items):
    objs = [{'z': BadHash(1)} for _ in range(n_items)]
    hi = index_type(objs, ['z'])
    for o in objs:
        o['z'] = BadHash(2)  # we didn't call update()
    hi.find({'z': BadHash(1)})


@pytest.mark.parametrize('n_items', [5, SIZE_THRESH+1])
def test_remove_stale_objects(n_items):
    objs = [{'z': BadHash(1)} for _ in range(n_items)]
    hi = HashIndex(objs, ['z'])
    for o in objs:
        o['z'] = BadHash(2)  # we didn't call update()
    hi.remove(objs[0])


@pytest.mark.parametrize('n_items', [5, SIZE_THRESH+1])
def test_remove_missing_object(n_items):
    objs = [{'z': BadHash(1)} for _ in range(n_items)]
    hi = HashIndex(objs, ['z'])
    hi.remove(BadHash(2))
