
def test_eq_and_greater(box_class):
    objs = [{'x': i} for i in range(10)]
    fb = box_class(objs, 'x')
    assert fb.find({'x': {'==': 1, '>': 0}}) == [objs[1]]


def test_eq_and_in(box_class):
    objs = [{'x': i} for i in range(10)]
    fb = box_class(objs, 'x')
    assert fb.find({'x': {'eq': 1, 'in': [1, 2, 3]}}) == [objs[1]]


def test_greater_less_and_in(box_class):
    objs = [{'x': i} for i in range(10)]
    fb = box_class(objs, 'x')
    assert len(fb.find({'x': {'gt': 1, 'lt': 5, 'in': [1, 2, 3]}})) == 2


def test_gte_lte_in_and_eq(box_class):
    objs = [{'x': i} for i in range(10)]
    fb = box_class(objs, 'x')
    assert len(fb.find({'x': {'gte': 1, 'lte': 5, 'in': [1, 2, 3], 'eq': 2}})) == 1
