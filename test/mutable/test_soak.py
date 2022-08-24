"""
DBox (mutable form) is pretty complex.
Let's run a lengthy test to make sure all the pieces work as expected across many add / remove operations.
"""

import random
import time
from datetime import datetime
from dbox import DBox
from dbox.utils import get_attribute


PLANETS = (
    ["mercury"] * 1
    + ["venus"] * 2
    + ["earth"] * 4
    + ["mars"] * 8
    + ["jupiter"] * 16
    + ["saturn"] * 32
    + ["uranus"] * 64
    + ["neptune"] * 128
)


class Collider:

    VALS = list(range(10))

    def __init__(self):
        self.n = random.choice(self.VALS)

    def __hash__(self):
        return self.n % 2

    def __eq__(self, other):
        return self.n == other.n

    def __lt__(self, other):
        return self.n < other.n


class Thing:
    def __init__(self, id_num):
        self.id_num = id_num
        self.ts_sec = datetime.now().replace(microsecond=0)
        self.ts = datetime.now()
        self.planet = random.choice(PLANETS)
        self.collider = Collider()
        if random.random() > 0.5:
            self.sometimes = True


def planet_len(obj):
    if isinstance(obj, dict):
        return len(obj["planet"])
    else:
        return len(obj.planet)


def make_dict_thing(id_num):
    t = Thing(id_num)
    return {
        "id_num": t.id_num,
        "ts_sec": t.ts_sec,
        "ts": t.ts,
        "planet": t.planet,
        "collider": t.collider,
        planet_len: planet_len(t),
    }


class SoakTest:
    """
    Keep running insert / update / remove operations at random for a long time.
    Check periodically to make sure[] results are correct.
    """

    def __init__(self):
        self.t0 = time.time()
        self.t_report = set([5 * i for i in range(1000)])
        random.seed(time.time())
        self.seed = random.choice(range(10 ** 6))
        print("running soak test with seed:", self.seed)
        random.seed(self.seed)
        self.f = DBox(
            on=["ts_sec", "ts", "planet", "collider", "sometimes", planet_len]
        )
        #  self.f = DBox(on=[planet_len])
        self.objs = dict()
        self.max_id_num = 0

    def run(self, duration):
        while time.time() - self.t0 < duration:
            op = random.choice(
                [
                    self.add,
                    self.add_many,
                    self.remove,
                    self.remove_all,
                    self.check_equal,
                ]
            )
            op()

    def add(self):
        self.max_id_num += 1
        # randomly pick between a dict and a class instance
        if random.random() < 0.5:
            t = Thing(self.max_id_num)
        else:
            t = make_dict_thing(self.max_id_num)
        self.objs[self.max_id_num] = t
        self.f.add(t)

    def add_many(self):
        for _ in range(random.choice([10, 100, 1000])):
            self.add()

    def remove(self):
        if self.objs:
            key = random.choice(list(self.objs.keys()))
            obj = self.objs[key]
            self.f.remove(obj)
            del self.objs[key]

    def remove_all(self):
        for t in self.objs.values():
            self.f.remove(t)
        self.objs = dict()

    def remove_all_but_one(self):
        key = random.choice(list(self.objs.keys()))
        for k in self.objs:
            if k != key:
                self.f.remove(self.objs[k])
                del self.objs[k]

    def random_obj(self):
        if not len(self.objs):
            return None
        return random.choice(list(self.objs.values()))

    def check_equal(self):
        # check a string key
        ls = [
            o for o in self.objs.values() if get_attribute(o, "planet")[0] == "saturn"
        ]
        f_ls = self.f[{"planet": "saturn"}]
        assert len(ls) == len(f_ls)
        assert len(self.objs) == len(self.f._indexes["planet"])
        # check a functional key
        ls = [o for o in self.objs.values() if get_attribute(o, planet_len)[0] == 6]
        f_ls = self.f[{planet_len: 6}]
        assert len(ls) == len(f_ls)
        assert len(self.objs) == len(self.f._indexes[planet_len])
        # check a null-ish key
        ls = [
            o for o in self.objs.values() if get_attribute(o, "sometimes")[1] == False
        ]
        f_ls = self.f[{"sometimes": {'!=': True}}]
        assert len(ls) == len(f_ls)
        # check a colliding key
        c = Collider()
        ls = [o for o in self.objs.values() if get_attribute(o, "collider")[0] == c]
        f_ls = self.f[{"collider": c}]
        assert len(ls) == len(f_ls)
        assert len(self.objs) == len(self.f._indexes["collider"])
        # check an object-ish key
        t = self.random_obj()
        if t is not None:
            target_ts = get_attribute(t, "ts_sec")
            ls = [
                o
                for o in self.objs.values()
                if get_attribute(o, "ts_sec")[0] == target_ts[0]
            ]
            f_ls = self.f[{"ts_sec": target_ts[0]}]
            assert len(ls) == len(f_ls)


def test_soak():
    st = SoakTest()
    st.run(3)
