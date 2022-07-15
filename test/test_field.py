import random
import pytest
from hashindex.constants import SIZE_THRESH
from hashindex.mutable_field import MutableFieldIndex
from hashindex.frozen_field import FrozenFieldIndex
from hashindex.init_helpers import compute_buckets

from typing import List,Union, Callable, Any, Optional


class FieldWrapper:
    """
    A FieldIndex holds a reference an obj_map outside itself, so it needs a minimal wrapper for testing.
    """
    def __init__(self, field_index_class,
                 field: Union[str, Callable],
                 objs: Optional[List[Any]] = None):
        self.obj_map = {id(obj): obj for obj in objs} if objs else dict()
        if objs:
            bucket_plan = compute_buckets(objs, field, SIZE_THRESH)
            self.idx = field_index_class(field, self.obj_map, bucket_plan)
        else:
            self.idx = field_index_class(field, self.obj_map)

    def add(self, obj: Any):
        obj_id = id(obj)
        self.obj_map[obj_id] = obj
        self.idx.add(obj_id, obj)


class FloatObj:
    def __init__(self):
        self.s = random.random()


class StringObj:
    planets = ['mercury', 'venus', 'earth', 'mars'] + ['jupiter']*100 + ['saturn', 'uranus', 'neptune']

    def __init__(self):
        self.s = random.choice(self.planets)


def initialize_with_objs(idx_class, data_class):
    """Make a MutableFieldIndex and add items during init."""
    random.seed(42)
    things = [data_class() for _ in range(10 ** 3)]
    fw = FieldWrapper(idx_class, 's', things)
    return things, fw


def initialize_and_add(idx_class, data_class):
    random.seed(42)
    things = [data_class() for _ in range(10 ** 3)]
    fw = FieldWrapper(idx_class, 's')
    for thing in things:
        fw.add(thing)
    return things, fw


@pytest.fixture(params=[
        (MutableFieldIndex, initialize_with_objs),
        (MutableFieldIndex, initialize_and_add),
        # (FrozenFieldIndex, initialize_with_objs)
])
def idx_and_init(request):
    return request.param


@pytest.fixture(params=[FloatObj, StringObj])
def data_class(request):
    return request.param


def test_get_objs(idx_and_init, data_class):
    idx_class, init_fn = idx_and_init
    things, fw = init_fn(idx_class, data_class)
    result = fw.idx.get_objs(things[0].s)
    print(fw.idx.bucket_report())
    assert things[0] in result


def test_get_obj_id(idx_and_init, data_class):
    idx_class, init_fn = idx_and_init
    things, fw = init_fn(idx_class, data_class)
    result = fw.idx.get_obj_ids(things[0].s)
    print(fw.idx.bucket_report())
    assert id(things[0]) in result


def test_create_and_remove(data_class):
    things, fw = initialize_with_objs(MutableFieldIndex, data_class)
    for t in things:
        fw.idx.remove(id(t), t)
