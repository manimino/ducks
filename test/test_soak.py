"""
HashIndex (mutable form) is pretty complex.
Let's run a lengthy test to make sure all the pieces work as expected across many add / remove operations.
"""

import time
from datetime import datetime
import random
from hashindex import HashIndex


PLANETS = ['mercury'] * 1 + \
          ['venus'] * 2 + \
          ['earth'] * 4 + \
          ['mars'] * 8 + \
          ['jupiter'] * 16 + \
          ['saturn'] * 32 + \
          ['uranus'] * 64 + \
          ['neptune'] * 128


class Thing:
    def __init__(self):
        self.ts_sec = datetime.now().replace(microsecond=0)
        self.ts = datetime.now()
        self.planet = random.choice(PLANETS)
        self.n = random.random()
        if random.random() > 0.5:
            self.sometimes = True


class SoakTest:

    def __init__(self):
        self.t0 = time.time()
        self.seed = random.choice(range(1000))
        random.seed(self.seed)
        self.fp = lambda x: len(x.planet)
        self.hi = HashIndex(on=['ts_sec', 'ts', 'planet', 'n', 'sometimes', self.fp])
        self.objs = []

    def run(self, duration):
        while time.time() - self.t0 < duration:
            op = random.choice([self.add, self.add_many, self.remove, self.remove_all, self.check_equal])
            op()

    def add(self):
        t = Thing()
        self.objs.append(t)
        self.hi.add(t)

    def add_many(self):
        for _ in range(random.choice([10, 100, 1000])):
            self.add()

    def remove(self):
        if self.objs:
            obj = random.choice(self.objs)
            self.objs.remove(obj)
            self.hi.remove(obj)

    def remove_all(self):
        for t in self.objs:
            self.hi.remove(t)
        self.objs = []

    def check_equal(self):
        ls = [o for o in self.objs if o.planet == 'saturn']
        hi_ls = self.hi.find({'planet': 'saturn'})
        assert len(ls) == len(hi_ls)


def test_soak():
    st = SoakTest()
    st.run(5)