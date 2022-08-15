import pytest

from filterbox.btree import BTree
from .conftest import AssertRaises


@pytest.mark.parametrize(
    "expr, result",
    [
        ({">": 8}, [9]),
        ({">": 6}, [7, 8, 9]),
        ({"<": 1}, [0]),
        ({"<": 3}, [0, 1, 2]),
        ({">=": 9}, [9]),
        ({">=": 9, "<": 1}, []),
        ({">=": 5, "<": 6}, [5]),
        ({">=": 5, "<=": 5}, [5]),
        ({">": 6, "<=": 7}, [7]),
        ({">": 6, "<=": 8}, [7, 8]),
        ({">": 6, "<=": 6}, []),
        ({">=": 6, "<": 6}, []),
        ({">=": 999}, []),
        ({">": 999}, []),
        ({"<=": -1}, []),
        ({"<": -1}, []),
        ({">": 9.5}, []),
        ({">": 8.5, "<": 9.5}, [9]),
        ({">=": 7.5, "<=": 9.5}, [8, 9]),
        ({">": 4, "<": 3}, []),
        ({">=": 4, "<=": 3}, []),
        ({">=": 999, "<=": -1}, []),
        ({">": 999, "<": -1}, []),
        ({">": -100, "<": 100}, list(range(10))),
        ({">=": -100, "<=": 100}, list(range(10))),
    ],
)
def test_get_range_expr(expr, result):
    bt = BTree({i: i for i in range(10)})
    assert list(bt.get_range_expr(expr)) == result


def test_init_with_none():
    objs = {i: i for i in range(10)}
    objs[None] = 13
    with AssertRaises(TypeError):
        _ = BTree(objs)


def test_add_none():
    objs = {i: i for i in range(10)}
    bt = BTree(objs)
    with AssertRaises(TypeError):
        bt[None] = 13


def test_get():
    bt = BTree({1: "a"})
    assert bt.get(1) == "a"
    assert bt[1] == "a"
    assert bt.get(2) is None
    assert bt.get(3, 4) is 4


def test_get_empty():
    bt = BTree()
    assert len(bt.get_range_expr({">": 5})) == 0
    assert bt.get(3) is None
    assert bt.get(3, 45) == 45
    with AssertRaises(KeyError):
        _ = bt[3]


def test_len_full_init():
    bt = BTree({i: i for i in range(10)})
    assert len(bt) == 10
    del bt[0]
    assert len(bt) == 9
    bt[0] = 0
    assert len(bt) == 10
    bt[1] = 99  # key already present
    assert len(bt) == 10


def test_len_empty_init():
    bt = BTree()
    assert len(bt) == 0
    bt[0] = 0
    assert len(bt) == 1
    bt[0] = 99  # key already present
    assert len(bt) == 1
    del bt[0]
    assert len(bt) == 0


def test_keys_values():
    bt = BTree({"a": 1, "b": 2})
    assert list(bt.keys()) == ["a", "b"]
    assert list(bt.values()) == [1, 2]


def test_bad_expr():
    bt = BTree({"a": 1, "b": 2})
    with AssertRaises(ValueError):
        bt.get_range_expr({">": "a", ">=": "a"})
    with AssertRaises(ValueError):
        bt.get_range_expr({"<": "a", "<=": "a"})
    with AssertRaises(TypeError):
        bt.get_range_expr({"<=": 99})
