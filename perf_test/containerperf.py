import array
import random
import dataclasses
import sys
import time


@dataclasses.dataclass
class Thing:
    num: float


def make_a_thing():
    return Thing(random.random())


def make_array(n=1):
    a = array.array('Q')
    ls = []
    for i in range(n):
        t = make_a_thing()
        a.append(id(t))
        ls.append(t)
    return a, ls


def make_set(n=1):
    s = set()
    ls = []
    for i in range(n):
        t = make_a_thing()
        s.add(id(t))
        ls.append(t)
    return s, ls


def make_tuple(n=1):
    ls = [make_a_thing() for _ in range(n)]
    return tuple(id(o) for o in ls), ls


def main():
    for n in [1, 10, 25, 50, 75, 100, 110, 115, 120, 150, 200, 250, 500, 1000, 10**6]:
        a, junk1 = make_array(n)
        s, junk2 = make_set(n)
        t, junk3 = make_tuple(n)

        # check sizes
        print(f" === {n} items === ")
        #print('array size:', sys.getsizeof(a))
        print('tuple size:', sys.getsizeof(t))
        print('set size:', sys.getsizeof(s))

        # check lookups
        obj = make_a_thing()
        obj_id = id(obj)
        a.append(obj_id)
        s.add(obj_id)
        t = t + (obj_id,)

        t0 = time.time()
        _ = a.index(obj_id)
        t1 = time.time()
        _ = obj_id in s
        t2 = time.time()
        _ = t.index(obj_id)
        t3 = time.time()

        #print('array lookup (worst):', t1-t0)
        print('tuple lookup (worst):', t3-t2)
        print('set lookup:', t2-t1)

        # check add speed
        obj2 = make_a_thing()
        o2_id = id(obj2)
        t0 = time.time()
        a.append(o2_id)
        t1 = time.time()
        s.add(o2_id)
        t2 = time.time()
        t = t + (o2_id,)
        t3 = time.time()
        #print('array add:', t1-t0)
        print('tuple add:', t3-t2)
        print('set add:', t2-t1)



if __name__ == '__main__':
    main()