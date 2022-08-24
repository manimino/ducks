"""
None is a value that cannot be compared with <, > etc. But we definitely need
to support it as it's a common attribute value.
These tests check that None is handled properly.
"""

import pytest
from dbox import DBox
from dbox.constants import SET_SIZE_MIN, ARRAY_SIZE_MAX


def test_none(box_class):
    objs = [{"ok": i} for i in range(10)]
    objs.append({"ok": None})
    fb = box_class(objs, "ok")
    assert len(fb[{"ok": None}]) == 1


@pytest.mark.parametrize(
    "n_none", [1, ARRAY_SIZE_MAX - 1, ARRAY_SIZE_MAX + 1, SET_SIZE_MIN]
)
def test_add_remove_none(n_none):
    objs = [{"a": i} for i in range(10)]
    for i in range(n_none):
        objs.append({"a": None})
    fb = DBox(objs, "a")
    assert len(fb[{"a": [1, 2, None]}]) == 2 + n_none
    assert len(fb[{"a": [None]}]) == n_none
    fb.remove(objs[0])  # {'a': 0}
    fb.remove(objs[-1])  # {'a': None}
    assert len(fb) == len(objs) - 2
