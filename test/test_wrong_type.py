"""
Now that we're using trees, all objects have to be comparable, including the query values.
Try doing various bad things with types.
"""
import pytest

from filterbox.btree import BTree

from filterbox import FilterBox
from .conftest import AssertRaises


@pytest.mark.parametrize(
    "expr, expected, raises",
    [
        ("lol", 0, True),
        (["lol"], 0, True),
        ([1, "lol"], 1, True),
        ({"<": 3}, 3, False),
        (
            {"<": "lol"},
            0,
            True,
        ),  # todo implement frozen value based thing, then this will work
    ],
)
def test_find_wrong_type(box_class, expr, expected, raises):
    if type(expr) is list:
        # you can't write {'in': ['lol']} in a parametrize
        # other keys work, but not 'in'. It looks like parametrize must
        # be calling eval() or something. Pretty annoying.
        expr = {"in": expr}
    objs = [{"x": i} for i in range(10)]
    fb = box_class(objs, "x")
    if raises:
        with AssertRaises(TypeError):
            fb.find({"x": expr})
    else:
        assert len(fb.find({"x": expr})) == expected


def test_add_wrong_type():
    objs = [{"x": i} for i in range(10)]
    fb = FilterBox(objs, "x")
    assert len(fb._indexes["x"].tree) == 10
    with AssertRaises(TypeError):
        fb.add({"x": "lol"})
