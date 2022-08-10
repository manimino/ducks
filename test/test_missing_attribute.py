import pytest


from filterbox import ANY, FilterBox
from filterbox.exceptions import MissingAttribute
from filterbox.constants import SIZE_THRESH


@pytest.mark.parametrize("n_items", [1, 5, SIZE_THRESH + 1])
def test_missing_function(box_class, n_items):
    def even(obj):
        if obj % 2:
            raise MissingAttribute
        return True

    objs = range(n_items)
    fb = box_class(objs, [even])
    n_even = len([x for x in range(n_items) if x % 2 == 0])
    n_odd = n_items - n_even
    assert len(fb) == n_items
    assert len(fb.find(match={even: True})) == n_even
    assert len(fb.find(exclude={even: True})) == n_odd
    for idx in fb._indices.values():
        assert len(idx) == n_even


missing_attr_data = [
    {"a": 1, "b": 2},
    {"a": 3},
    {"b": 4},
    {},
]


def test_add_with_missing_attributes():
    fb = FilterBox([], ["a", "b"])
    for d in missing_attr_data:
        fb.add(d)
    assert len(fb) == 4
    assert len(fb._indices["a"]) == 2
    assert len(fb._indices["b"]) == 2
    assert len(fb.find(exclude={"b": {"in": [2, 4]}})) == 2
    assert len(fb.find(exclude={"a": {"in": [1, 3]}})) == 2


def test_remove_with_missing_attributes():
    fb = FilterBox(missing_attr_data, ["a", "b"])
    for d in missing_attr_data:
        fb.remove(d)
    assert len(fb) == 0
    for idx in fb._indices.values():
        assert len(idx) == 0


def test_missing_attributes(box_class):
    fb = box_class(missing_attr_data, ["a", "b"])
    for d in missing_attr_data:
        assert d in fb
    assert len(fb._indices["a"]) == 2
    assert len(fb._indices["b"]) == 2


def test_add_none():
    f = FilterBox(on="s")
    f.add(None)
    result = f.find({"s": None})
    assert result == []


def test_empty_attribute(box_class):
    fb = box_class([None], on=["a"])
    assert len(fb) == 1


def test_find_having_attr(box_class):
    fb = box_class(missing_attr_data, ["a", "b"])
    assert len(fb.find({"a": ANY})) == 2
    assert len(fb.find({"b": ANY})) == 2
    assert len(fb.find({"a": 1, "b": ANY})) == 1


def test_find_missing_attr(box_class):
    fb = box_class(missing_attr_data, ["a", "b"])
    assert len(fb.find(exclude={"a": ANY})) == 2
    assert len(fb.find(exclude={"b": ANY})) == 2
    assert len(fb.find(match={"a": 3}, exclude={"b": ANY})) == 1
    assert len(fb.find(exclude={"a": ANY, "b": ANY})) == 1


@pytest.mark.parametrize("n_items", [2, 10, SIZE_THRESH * 2 + 2])
def test_many_missing(box_class, n_items):
    data = []
    for i in range(n_items):
        if i % 2:
            data.append({"a": 1})
        else:
            data.append({})
    fb = box_class(data, ["a"])
    assert len(fb.find({"a": ANY})) == n_items // 2
    assert len(fb.find(exclude={"a": ANY})) == n_items // 2


@pytest.mark.parametrize("n_items", [2, 10, SIZE_THRESH * 2 + 2])
def test_get_values(box_class, n_items):
    data = []
    for i in range(n_items):
        if i % 2:
            data.append({"a": 1})
        else:
            data.append({})
    fb = box_class(data, ["a"])
    assert fb.get_values("a") == {1}
