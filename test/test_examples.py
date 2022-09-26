import random


def test_get_nearby(box_class):
    # set of tuples
    t = {(random.random() * 10, random.random() * 10) for _ in range(10**4)}

    def _x(obj):
        return int(obj[0])

    def _y(obj):
        return int(obj[1])

    f = box_class(t, [_x, _y])
    for pt in f[{_x: 0, _y: 0}]:
        assert _x(pt) < 1 and _y(pt) < 1


def test_wordle(box_class):
    ws = [
        ("ABOUT", 1226734006),
        ("OTHER", 978481319),
        ("WHICH", 810514085),
        ("THEIR", 782849411),
    ]

    def has_t(w):
        return "T" in w[0]

    def has_h(w):
        return "H" in w[0]

    f = box_class(ws, [has_t, has_h])
    found = f[{}]
    found_ws = [f[0] for f in found]
    for w in ws:
        assert w[0] in found_ws
