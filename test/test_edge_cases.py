from dbox import DBox
from dbox.constants import HASH_MIN, HASH_MAX, SIZE_THRESH
import pytest

from .conftest import AssertRaises, BadHash


class EdgeHash:
    HASHES = [HASH_MIN, 0, HASH_MAX]

    def __init__(self, x: int):
        self.x = x

    def __hash__(self):
        return self.HASHES[self.x % 3]

    def __eq__(self, other):
        return self.x == other.x

    def __lt__(self, other):
        return self.x < other.x


@pytest.mark.parametrize("n_items", [SIZE_THRESH * 3 + 3, 15])
def test_edge_hash(box_class, n_items):
    f = box_class([{"z": EdgeHash(i % 3)} for i in range(n_items)], ["z"])
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

    f = DBox(on=["z"])
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

    def __lt__(self, other):
        return self.x < other.x


@pytest.mark.parametrize("delete_bucket", [0, 1, 2])
def test_grouped_hash(delete_bucket):
    arrs = [list(), list(), list()]
    for i in range(SIZE_THRESH * 3 + 3):
        arrs[i % 3].append({"z": GroupedHash(i % 3)})

    f = DBox(on=["z"])
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


def test_get_zero(box_class):
    def _f(x):
        return x[0]

    f = box_class(["a", "b", "c"], on=[_f])
    assert f.find({_f: "c"}) == ["c"]
    assert len(f.find({_f: "d"})) == 0


def test_get_in_no_results(box_class):
    def _f(x):
        return x[0]

    f = box_class(["a", "b", "c"], on=[_f])
    assert len(f.find({_f: {"in": ["d"]}})) == 0
    assert len(f.find({_f: {"in": []}})) == 0


def test_double_add():
    f = DBox(on="s")
    x = {"s": "hello"}
    f.add(x)
    f.add(x)
    assert len(f) == 1
    assert f.find({"s": "hello"}) == [x]
    f.remove(x)
    assert len(f) == 0
    assert f.find({"s": "hello"}) == []


def test_empty_index(box_class):
    f = box_class([], on=["stuff"])
    result = f.find({"stuff": 3})
    assert len(result) == 0
    result = f.find({"stuff": {"<": 3}})
    assert len(result) == 0


def test_arg_order():
    data = [{"a": i % 5, "b": i % 3} for i in range(100)]
    f = DBox(data, ["a", "b"])
    assert len(f.find({"a": 1, "b": 2})) == len(f.find({"b": 2, "a": 1}))


class NoSort:
    def __init__(self, x):
        self.x = x

    def __hash__(self):
        return hash(self.x)

    def __eq__(self, other):
        return self.x == other.x


def test_unsortable_values(box_class):
    """We need to support values that are hashable, even if they cannot be sorted."""
    objs = [{"a": NoSort(0)}, {"a": NoSort(1)}]
    with AssertRaises(TypeError):
        box_class(objs, ["a"])


def test_not_in(box_class):
    """the things we do for 100% coverage"""
    f = box_class([{"a": 1}], on=["a"])
    assert {"a": 0} not in f
    assert {"a": 2} not in f


def test_external_object_modification(box_class):
    """
    What happens if the values are mutable, and someone mutates them externally?
    Answer: It screws everything up.
    But it *also* screws up Python's own set and frozenset containers, so... I think we don't need
    to go all the way into doing deepcopy() on every object we store. "Consenting adults", etc.
    At some point it's up to the user not to do weird stuff.
    Mutable + Hashable objects are big trouble -- there's a reason Python primitives are only ever one of the two.
    """
    objs = [{"a": BadHash(1)}]
    fb = box_class(objs, "a")
    assert len(fb.find({"a": BadHash(1)})) == 1
    objs[0]["a"].n = 5000
    # external modification changed our results
    assert len(fb.find({"a": BadHash(1)})) == 0


def test_in_with_greater(box_class):
    """
    Technically someone could query a '<' along with an 'in'. Does that work properly?
    """
    f = box_class([{"a": 1}], on="a")
    assert len(f.find({"a": {"<=": 1, "in": [1]}})) == 1
    assert len(f.find({"a": {">": 1, "in": [1]}})) == 0
    assert len(f.find({"a": {"<=": 1, "in": [0]}})) == 0
    assert len(f.find({"a": {"<": 1, "in": [0]}})) == 0
