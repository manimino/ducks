from dbox import DBox

from .conftest import AssertRaises


def test_get_zero(box_class):
    def _f(x):
        return x[0]

    f = box_class(["a", "b", "c"], on=[_f])
    assert f[{_f: "c"}] == ["c"]
    assert len(f[{_f: "d"}]) == 0


def test_get_in_no_results(box_class):
    def _f(x):
        return x[0]

    f = box_class(["a", "b", "c"], on=[_f])
    assert len(f[{_f: {"in": ["d"]}}]) == 0
    assert len(f[{_f: {"in": []}}]) == 0


def test_double_add():
    f = DBox(on="s")
    x = {"s": "hello"}
    f.add(x)
    f.add(x)
    assert len(f) == 1
    assert f[{"s": "hello"}] == [x]
    f.remove(x)
    assert len(f) == 0
    assert f[{"s": "hello"}] == []


def test_empty_index(box_class):
    f = box_class([], on=["stuff"])
    result = f[{"stuff": 3}]
    assert len(result) == 0
    result = f[{"stuff": {"<": 3}}]
    assert len(result) == 0


def test_arg_order():
    data = [{"a": i % 5, "b": i % 3} for i in range(100)]
    f = DBox(data, ["a", "b"])
    assert len(f[{"a": 1, "b": 2}]) == len(f[{"b": 2, "a": 1}])


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


def test_in_with_greater(box_class):
    """
    Technically someone could query a '<' along with an 'in'. Does that work properly?
    """
    f = box_class([{"a": 1}], on="a")
    assert len(f[{"a": {"<=": 1, "in": [1]}}]) == 1
    assert len(f[{"a": {">": 1, "in": [1]}}]) == 0
    assert len(f[{"a": {"<=": 1, "in": [0]}}]) == 0
    assert len(f[{"a": {"<": 1, "in": [0]}}]) == 0
