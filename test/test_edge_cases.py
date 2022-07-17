from hashindex import HashIndex, FrozenHashIndex
from hashindex.exceptions import MissingObjectError
import unittest


def test_get_zero(index_type):
    def _f(x):
        return x[0]

    hi = index_type(["a", "b", "c"], on=[_f])
    assert hi.find({_f: "c"}) == ["c"]
    assert len(hi.find({_f: "d"})) == 0


def test_add_none():
    hi = HashIndex(on='s')
    hi.add(None)
    result = hi.find({'s': None})
    assert result[0] is None


def test_double_add():
    hi = HashIndex(on='s')
    x = {'s': 'hello'}
    hi.add(x)
    hi.add(x)
    assert len(hi) == 1
    assert hi.find({'s': 'hello'}) == [x]
    hi.remove(x)
    assert len(hi) == 0
    assert hi.find({'s': 'hello'}) == []


def test_empty_mutable_index():
    hi = HashIndex([], on=["stuff"])
    result = hi.find({"stuff": 3})
    assert len(result) == 0


class TestExceptions(unittest.TestCase):
    def test_remove_empty(self):
        hi = HashIndex([], on=["stuff"])
        with self.assertRaises(MissingObjectError):
            hi.remove("nope")

    def test_empty_frozen(self):
        with self.assertRaises(ValueError):
            FrozenHashIndex([], on=["stuff"])
