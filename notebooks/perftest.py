import random
import time
from dataclasses import dataclass
from filtered import Filtered

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


def make_objs(n_keys, n_items):
    ls = []
    for _ in range(n_items):
        i = int(
            random.random() * random.random() * n_keys
        )  # keys are mostly low numbers
        ls.append(
            Obj(
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
            )
        )
    return ls


def perf_test(size=100000, n_indices=1):
    print(f"=== Filtered Test: {size} items, {n_indices} indices ===")
    TARGET = str(1)

    # About 10% of the objs will have the first key
    # A long tail of keys will have fewer objs each
    ls = make_objs(int(size ** (1 / 3)), size)

    attribs = Obj.__annotations__.keys()
    indices = []
    for i, k in enumerate(attribs):
        if i >= n_indices:
            break
        indices.append(k)

    d = {}
    for o in ls:
        if not d.get(o.f, None):
            d[o.f] = []
        d[o.f].append(o)
    print("n_keys", len(d.keys()))
    # for k in sorted(d.keys()):
    #    print(k, len(d[k]))

    # build Filtered
    t0 = time.time()
    hi = Filtered(indices)
    for item in ls:
        hi.add(item)
    t_hashbox_build = time.time() - t0
    print("Build time:", round(t_hashbox_build, 6))

    # index lookup
    t0 = time.time()
    _ = hi.find({"a": TARGET})[0]
    t_hashbox = time.time() - t0
    print("Filtered Find:", round(t_hashbox, 6))

    objs_size = asizeof.asizeof(ls)
    hi_size = asizeof.asizeof(hi)
    print("Mem cost:", (hi_size - objs_size) // 10 ** 6, "MB")
    time.sleep(5)


if __name__ == "__main__":
    perf_test(size=10 ** 5, n_indices=1)
    perf_test(size=10 ** 5, n_indices=10)
    perf_test(size=10 ** 6, n_indices=1)
