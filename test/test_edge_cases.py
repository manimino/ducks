from hashindex import HashIndex

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
