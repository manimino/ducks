from hashindex import HashIndex, FrozenHashIndex
from hashindex.exceptions import MissingObjectError
import unittest


# TODO:
# Can we correctly match / mismatch None values?
# What happens when the user forgets to remove / update an object?
# What if I add an object twice? Is it rejected?
# test getting with expected 0 items and 1 item


def test_get_zero():
    def _f(x):
        return x[0]
    hi = HashIndex(['a', 'b', 'c'], on=[_f])
    assert hi.find({_f: 'c'}) == ['c']
    assert hi.find({_f: 'd'}) == []


def test_empty_index(index_type):
    hi = index_type([], on=['stuff'])
    result = hi.find({'stuff': 3})
    assert len(result) == 0


class TestExceptions(unittest.TestCase):

    def test_remove_empty(self):
        for index_type in [HashIndex, FrozenHashIndex]:
            hi = index_type([], on=['stuff'])
            with self.assertRaises(MissingObjectError):
                hi.remove('nope')
