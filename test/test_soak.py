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
        self.planet = random.choice(PLANETS)
        self.n = random.random()
        if random.random() > 0.5:
            self.sometimes = True


class SoakTest:

    def __init__(self):
        self.t0 = time.time()
        self.seed = random.choice(range(1000))
        random.seed(self.seed)
        self.hi = HashIndex()

    def add(self, n):
        pass

    def remove(self):
        pass
