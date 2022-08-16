"""
None is a value that cannot be compared with <, > etc. But we definitely need
to support it as it's a common attribute value.
These tests check that None is handled properly.
"""


def test_none(box_class):
    objs = [{"ok": i} for i in range(10)]
    objs.append({"ok": None})
    fb = box_class(objs, "ok")
    assert len(fb.find({"ok": None})) == 1

