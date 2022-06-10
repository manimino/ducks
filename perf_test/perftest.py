import time
from dataclasses import dataclass
from hashindex.hashindex import HashIndex

from pympler import asizeof


# Graphs we want:
# - RAM usage
# -- Determine the summed size of the objects
# -- Find overhead of a `list` containing the objects
# -- Find cost of a

@dataclass
class Obj:
    a: str
    b: str
    c: str
    d: str
    e: str
    f: int
    g: int
    h: int
    i: int
    j: int


def make_objs(n):
    ls = []
    for i in range(10000):  # hackery to test dict density here
        for i in range(n//10000):
            ls.append(Obj(
                a=str(i),
                b=str(i),
                c=str(i),
                d=str(i),
                e=str(i),
                f=i,
                g=i,
                h=i,
                i=i,
                j=i,
            ))
    return ls


def perf_test(size=100000, n_indices=1):
    print(f"=== MatchIndex Test: {size} items, {n_indices} indices ===")
    TARGET = str(1)

    ls = make_objs(size)

    attribs = Obj.__annotations__.keys()
    indices = []
    for i, k in enumerate(attribs):
        if i >= n_indices:
            break
        indices.append(k)

    # build MatchIndex
    t0 = time.time()
    box = HashIndex(indices)
    for item in ls:
        box.add(item)
    t_hashbox_build = time.time() - t0
    print('MatchIndex Make:', round(t_hashbox_build, 6))

    # linear search
    t0 = time.time()
    ls_item = None
    for item in ls:
        if item.a == TARGET:
            ls_item = item
            break
    t_linear = time.time() - t0
    print('Linear Find: ', round(t_linear, 6))

    # index lookup
    t0 = time.time()
    box_item = box.find({'a': TARGET})[0]
    t_hashbox = time.time() - t0
    print('MatchIndex Find:', round(t_hashbox, 6))
    assert ls_item == box_item  # correctness

    print('List mem size:   ', asizeof.asizeof(ls))
    print('MatchIndex mem size:', asizeof.asizeof(box))
    time.sleep(5)


if __name__ == '__main__':
    perf_test()
    perf_test(size=1000000, n_indices=10)