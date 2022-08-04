import pytest


from hashbox import ANY, HashBox
from hashbox.exceptions import MissingAttribute
from hashbox.constants import SIZE_THRESH


@pytest.mark.parametrize("n_items", [1, 5, SIZE_THRESH + 1])
def test_missing_function(box_class, n_items):
    def even(obj):
        if obj % 2:
            raise MissingAttribute
        return True

    objs = range(n_items)
    hb = box_class(objs, [even])
    n_even = len([x for x in range(n_items) if x % 2 == 0])
    n_odd = n_items - n_even
    assert len(hb) == n_items
    assert len(hb.find(match={even: True})) == n_even
    assert len(hb.find(exclude={even: True})) == n_odd
    for idx in hb.indices.values():
        assert len(idx) == n_even


missing_attr_data = [
    {"a": 1, "b": 2},
    {"a": 3},
    {"b": 4},
    {},
]


def test_add_with_missing_attributes():
    hb = HashBox([], ["a", "b"])
    for d in missing_attr_data:
        hb.add(d)
    assert len(hb) == 4
    assert len(hb.indices["a"]) == 2
    assert len(hb.indices["b"]) == 2
    assert len(hb.find(exclude={"b": [2, 4]})) == 2
    assert len(hb.find(exclude={"a": [1, 3]})) == 2


def test_remove_with_missing_attributes():
    hb = HashBox(missing_attr_data, ["a", "b"])
    for d in missing_attr_data:
        hb.remove(d)
    assert len(hb) == 0
    for idx in hb.indices.values():
        assert len(idx) == 0


def test_missing_attributes(box_class):
    hb = box_class(missing_attr_data, ["a", "b"])
    for d in missing_attr_data:
        assert d in hb
    assert len(hb.indices["a"]) == 2
    assert len(hb.indices["b"]) == 2


def test_add_none():
    f = HashBox(on="s")
    f.add(None)
    result = f.find({"s": None})
    assert result == []


def test_empty_attribute(box_class):
    hb = box_class([None], on=["a"])
    assert len(hb) == 1


def test_find_having_attr(box_class):
    hb = box_class(missing_attr_data, ["a", "b"])
    assert len(hb.find({'a': ANY})) == 2
    assert len(hb.find({'b': ANY})) == 2
    assert len(hb.find({'a': 1, 'b': ANY})) == 1


def test_find_missing_attr(box_class):
    hb = box_class(missing_attr_data, ["a", "b"])
    assert len(hb.find(exclude={'a': ANY})) == 2
    assert len(hb.find(exclude={'b': ANY})) == 2
    assert len(hb.find(match={'a': 3}, exclude={'b': ANY})) == 1
    assert len(hb.find(exclude={'a': ANY, 'b': ANY})) == 1


@pytest.mark.parametrize('n_items', [2, 10, SIZE_THRESH*2+2])
def test_many_missing(box_class, n_items):
    data = []
    for i in range(n_items):
        if i % 2:
            data.append({'a': 1})
        else:
            data.append({})
    hb = box_class(data, ["a"])
    assert len(hb.find({'a': ANY})) == n_items // 2
    assert len(hb.find(exclude={'a': ANY})) == n_items // 2


@pytest.mark.parametrize('n_items', [2, 10, SIZE_THRESH*2+2])
def test_get_values(box_class, n_items):
    data = []
    for i in range(n_items):
        if i % 2:
            data.append({'a': 1})
        else:
            data.append({})
    hb = box_class(data, ["a"])
    assert hb.get_values('a') == {1}
