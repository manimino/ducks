"""
Now that we're using trees, all objects have to be comparable, including the query values.
Try doing various bad things with types.
"""
import pytest

from BTrees.OOBTree import OOBTree

from filterbox import FilterBox


@pytest.mark.parametrize(
    'expr, expected',
    [
        ['lol', 0],
        [['lol'], 0],
        [[1, 'lol'], 1],
        [{'<': 3}, 3],
        [{'<': 'lol'}, 0],
    ])
def test_find_wrong_type(box_class, expr, expected):
    if type(expr) is list:
        # you can't write {'in': ['lol']} in a parametrize
        # other keys work, but not 'in'. It looks like parametrize must
        # be calling eval() or something. Pretty annoying.
        expr = {'in': expr}
    objs = [{'x': i} for i in range(10)]
    fb = box_class(objs, 'x')
    assert len(fb.find({'x': expr})) == expected


def test_add_wrong_type():
    # degrades to dict when there's a type conflict. idk if this is a good idea but w/e
    objs = [{'x': i} for i in range(10)]
    fb = FilterBox(objs, 'x')
    assert type(fb._indices['x'].d) is OOBTree
    assert len(fb._indices['x'].d) == 10
    fb.add({'x': 'lol'})
    assert type(fb._indices['x'].d) is dict
    assert len(fb._indices['x'].d) == 11
