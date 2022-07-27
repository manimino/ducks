from filtered import Filtered
from filtered.constants import HASH_MIN, HASH_MAX, SIZE_THRESH
import pytest


class EdgeHash:
    HASHES = [HASH_MIN, 0, HASH_MAX]

    def __init__(self, x: int):
        self.x = x

    def __hash__(self):
        return self.HASHES[self.x % 3]

    def __eq__(self, other):
        return self.x == other.x


@pytest.mark.parametrize("n_items", [SIZE_THRESH * 3 + 3, 15])
def test_edge_hash(index_type, n_items):
    f = index_type([{"z": EdgeHash(i % 3)} for i in range(n_items)], ["z"])
    assert len(f.find({"z": EdgeHash(0)})) == n_items // 3
    assert len(f.find({"z": EdgeHash(1)})) == n_items // 3
    assert len(f.find({"z": EdgeHash(2)})) == n_items // 3


@pytest.mark.parametrize(
    "n_items,delete_bucket",
    [
        (SIZE_THRESH * 3 + 3, 0),
        (SIZE_THRESH * 3 + 3, 1),
        (SIZE_THRESH * 3 + 3, 2),
        (15, 0),
        (15, 1),
        (15, 2),
    ],
)
def test_edge_hash_mutable(n_items, delete_bucket):
    """Ensure there are no problems creating / destroying buckets at the extrema of the hash space."""
    arrs = [list(), list(), list()]
    for i in range(n_items):
        arrs[i % 3].append({"z": EdgeHash(i % 3)})

    f = Filtered(on=["z"])
    for arr in arrs:
        for obj in arr:
            f.add(obj)
    for obj in arrs[delete_bucket]:
        f.remove(obj)
    assert len(f.find()) == int(n_items * 2 / 3)
    for i in range(3):
        if i == delete_bucket:
            continue
        for obj in arrs[i]:
            f.remove(obj)
    assert len(f) == 0


class GroupedHash:
    HASHES = [1, 2, 3]

    def __init__(self, x: int):
        self.x = x

    def __hash__(self):
        return self.HASHES[self.x % 3]

    def __eq__(self, other):
        return self.x == other.x


@pytest.mark.parametrize("delete_bucket", [0, 1, 2])
def test_grouped_hash(delete_bucket):
    arrs = [list(), list(), list()]
    for i in range(SIZE_THRESH * 3 + 3):
        arrs[i % 3].append({"z": GroupedHash(i % 3)})

    f = Filtered(on=["z"])
    for arr in arrs:
        for gh in arr:
            f.add(gh)

    # That created three adjacent DictBuckets. Now let's get rid of the delete_bucket.
    for obj in arrs[delete_bucket]:
        f.remove(obj)

    for b in range(3):
        if b == delete_bucket:
            assert len(f.find({"z": GroupedHash(b)})) == 0
        else:
            assert len(f.find({"z": GroupedHash(b)})) == SIZE_THRESH + 1


def test_get_zero(index_type):
    def _f(x):
        return x[0]

    f = index_type(["a", "b", "c"], on=[_f])
    assert f.find({_f: "c"}) == ["c"]
    assert len(f.find({_f: "d"})) == 0


def test_add_none():
    f = Filtered(on="s")
    f.add(None)
    result = f.find({"s": None})
    assert result[0] is None


def test_double_add():
    f = Filtered(on="s")
    x = {"s": "hello"}
    f.add(x)
    f.add(x)
    assert len(f) == 1
    assert f.find({"s": "hello"}) == [x]
    f.remove(x)
    assert len(f) == 0
    assert f.find({"s": "hello"}) == []


def test_empty_mutable_index():
    f = Filtered([], on=["stuff"])
    result = f.find({"stuff": 3})
    assert len(result) == 0


def test_arg_order():
    data = [{"a": i % 5, "b": i % 3} for i in range(100)]
    f = Filtered(data, ["a", "b"])
    assert len(f.find({"a": 1, "b": 2})) == len(f.find({"b": 2, "a": 1}))


class NoSort:
    def __init__(self, x):
        self.x = x

    def __hash__(self):
        return hash(self.x)

    def __eq__(self, other):
        return self.x == other.x


def test_unsortable_values(index_type):
    """We need to support values that are hashable, even if they cannot be sorted."""
    objs = [{"a": NoSort(0)}, {"a": NoSort(1)}]
    f = index_type(objs, ["a"])
    if isinstance(index_type, Filtered):
        objs.append(NoSort(2))
        f.add(objs[2])
    assert len(f) == len(objs)
    for i, obj in enumerate(objs):
        assert f.find({"a": NoSort(i)}) == [obj]


def test_not_in(index_type):
    """the things we do for 100% coverage"""
    f = index_type([{"a": 1}], on=["a"])
    assert {"a": 0} not in f
    assert {"a": 2} not in f
