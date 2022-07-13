import random
from hashindex.mutable_field import MutableFieldIndex


class Thing:
    def __init__(self):
        self.s = random.random()


def make_index():
    random.seed(42)
    things = [Thing() for _ in range(10 ** 3)]
    mf = MutableFieldIndex('s')
    for thing in things:
        mf.add(id(thing), thing)
    return things, mf


def test_get_objs():
    things, mf = make_index()
    result = mf.get_objs(things[0].s)
    assert things[0] in result


def test_get_obj_id():
    things, mf = make_index()
    result = mf.get_obj_ids(things[0].s)
    assert id(things[0]) in result
