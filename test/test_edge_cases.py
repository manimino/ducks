from hashindex import HashIndex
from hashindex.constants import HASH_MIN, HASH_MAX, SIZE_THRESH
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
    hi = index_type([{"z": EdgeHash(i % 3)} for i in range(n_items)], ["z"])
    assert len(hi.find({"z": EdgeHash(0)})) == n_items // 3
    assert len(hi.find({"z": EdgeHash(1)})) == n_items // 3
    assert len(hi.find({"z": EdgeHash(2)})) == n_items // 3


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

    hi = HashIndex(on=["z"])
    for arr in arrs:
        for obj in arr:
            hi.add(obj)
    for obj in arrs[delete_bucket]:
        hi.remove(obj)
    assert len(hi.find()) == int(n_items * 2 / 3)
    for i in range(3):
        if i == delete_bucket:
            continue
        for obj in arrs[i]:
            hi.remove(obj)
    assert len(hi) == 0


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

    hi = HashIndex(on=["z"])
    for arr in arrs:
        for gh in arr:
            hi.add(gh)

    # That created three adjacent DictBuckets. Now let's get rid of the delete_bucket.
    for obj in arrs[delete_bucket]:
        hi.remove(obj)

    for b in range(3):
        if b == delete_bucket:
            assert len(hi.find({"z": GroupedHash(b)})) == 0
        else:
            assert len(hi.find({"z": GroupedHash(b)})) == SIZE_THRESH + 1


def test_get_zero(index_type):
    def _f(x):
        return x[0]

    hi = index_type(["a", "b", "c"], on=[_f])
    assert hi.find({_f: "c"}) == ["c"]
    assert len(hi.find({_f: "d"})) == 0


def test_add_none():
    hi = HashIndex(on="s")
    hi.add(None)
    result = hi.find({"s": None})
    assert result[0] is None


def test_double_add():
    hi = HashIndex(on="s")
    x = {"s": "hello"}
    hi.add(x)
    hi.add(x)
    assert len(hi) == 1
    assert hi.find({"s": "hello"}) == [x]
    hi.remove(x)
    assert len(hi) == 0
    assert hi.find({"s": "hello"}) == []


def test_empty_mutable_index():
    hi = HashIndex([], on=["stuff"])
    result = hi.find({"stuff": 3})
    assert len(result) == 0


def test_arg_order():
    data = [{"a": i % 5, "b": i % 3} for i in range(100)]
    hi = HashIndex(data, ["a", "b"])
    assert len(hi.find({"a": 1, "b": 2})) == len(hi.find({"b": 2, "a": 1}))


class NoSort:
    def __init__(self, x):
        self.x = x

    def __hash__(self):
        return hash(self.x)

    def __eq__(self, other):
        return self.x == other.x


def test_unsortable_values(index_type):
    """We need to support values that are hashable, even if they cannot be sorted."""
    objs = [{'a': NoSort(0)}, {'a': NoSort(1)}]
    hi = index_type(objs, ['a'])
    if isinstance(index_type, HashIndex):
        objs.append(NoSort(2))
        hi.add(objs[2])
    assert len(hi) == len(objs)
    for i, obj in enumerate(objs):
        assert hi.find({'a': NoSort(i)}) == [obj]
