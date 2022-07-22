import random


def test_get_nearby(index_type):
    t = {(random.random() * 10, random.random() * 10) for _ in range(10 ** 4)}

    def _x(obj):
        return int(obj[0])

    def _y(obj):
        return int(obj[1])

    hi = index_type(t, [_x, _y])
    for pt in hi.find({_x: 0, _y: 0}):
        assert _x(pt) < 1 and _y(pt) < 1
