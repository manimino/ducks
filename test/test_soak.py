"""
HashIndex (mutable form) is pretty complex.
Let's run a lengthy test to make sure all the pieces work as expected across many add / remove operations.
"""

import time
from datetime import datetime
import random
from hashindex import HashIndex
from hashindex.utils import get_field


PLANETS = ['mercury'] * 1 + \
          ['venus'] * 2 + \
          ['earth'] * 4 + \
          ['mars'] * 8 + \
          ['jupiter'] * 16 + \
          ['saturn'] * 32 + \
          ['uranus'] * 64 + \
          ['neptune'] * 128


class Thing:
    def __init__(self, id_num):
        self.id_num = id_num
        self.ts_sec = datetime.now().replace(microsecond=0)
        self.ts = datetime.now()
        self.planet = random.choice(PLANETS)
        self.n = random.random()
        if random.random() > 0.5:
            self.sometimes = True


def planet_len(obj):
    if isinstance(obj, dict):
        return len(obj['planet'])
    else:
        return len(obj.planet)


def make_dict_thing(id_num):
    t = Thing(id_num)
    return {
        'id_num': t.id_num,
        'ts_sec': t.ts_sec,
        'ts': t.ts,
        'planet': t.planet,
        'n': t.n,
        planet_len: planet_len(t)
    }


class SoakTest:

    def __init__(self):
        self.t0 = time.time()
        self.seed = random.choice(range(1000))
        random.seed(self.seed)
        self.hi = HashIndex(on=['ts_sec', 'ts', 'planet', 'n', 'sometimes', planet_len])
        #  self.hi = HashIndex(on=[planet_len])
        self.objs = dict()
        self.max_id_num = 0

    def run(self, duration):
        while time.time() - self.t0 < duration:
            op = random.choice([self.add, self.add_many, self.remove, self.remove_all, self.check_equal])
            try:
                op()
            except KeyError as e:
                print(len(self.objs), 'remaining')
                raise e

    def add(self):
        self.max_id_num += 1
        # randomly pick between a dict and a class instance
        if random.random() < 0.5:
            t = Thing(self.max_id_num)
        else:
            t = make_dict_thing(self.max_id_num)
        self.objs[self.max_id_num] = t
        self.hi.add(t)

    def add_many(self):
        for _ in range(random.choice([10, 100, 1000])):
            self.add()

    def remove(self):
        if self.objs:
            key = random.choice(list(self.objs.keys()))
            obj = self.objs[key]
            self.hi.remove(obj)
            del self.objs[key]

    def remove_all(self):
        for t in self.objs.values():
            self.hi.remove(t)
        self.objs = dict()

    def check_equal(self):
        ls = [o for o in self.objs.values() if get_field(o, 'planet') == 'saturn']
        hi_ls = self.hi.find({'planet': 'saturn'})
        assert len(ls) == len(hi_ls)
        ls = [o for o in self.objs.values() if get_field(o, planet_len) == 6]
        hi_ls = self.hi.find({planet_len: 6})
        assert len(ls) == len(hi_ls)


def test_soak():
    st = SoakTest()
    st.run(60)
