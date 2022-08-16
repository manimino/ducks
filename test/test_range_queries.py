import pytest

from filterbox.constants import SIZE_THRESH


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
def test_get_range_expr(box_class, expr, result):
    objs = [{"a": i} for i in range(10)] + [{'a': None}]
    fb = box_class(objs, "a")
    assert list(sorted(o["a"] for o in fb.find({"a": expr}))) == result


@pytest.mark.parametrize(
    "expr",
    [
        {">": 8},
        {">": 6},
        {"<": 1},
        {"<": 3},
        {">=": 9},
        {">=": 9, "<": 1},
        {">=": 5, "<": 6},
        {">=": 5, "<=": 5},
        {">": 6, "<=": 7},
        {">": 6, "<=": 8},
        {">": 6, "<=": 6},
        {">=": 6, "<": 6},
        {">=": 999},
        {">": 999},
        {"<=": -1},
        {"<": -1},
        {">": 9.5},
        {">": 8.5, "<": 9.5},
        {">=": 7.5, "<=": 9.5},
        {">": 4, "<": 3},
        {">=": 4, "<=": 3},
        {">=": 999, "<=": -1},
        {">": 999, "<": -1},
        {">": -100, "<": 100},
        {">=": -100, "<=": 100},
    ],
)
def test_get_big(box_class, expr):
    objs = [{"a": i % 10} for i in range(SIZE_THRESH * 11)]
    objs += [{"a": None} for _ in range(SIZE_THRESH + 1)]
    fb = box_class(objs, "a")
    found = fb.find({"a": expr})
    result = [o for o in objs if o['a'] is not None]
    for op, val in expr.items():
        if op == ">":
            result = [o for o in result if o["a"] > val]
        if op == "<":
            result = [o for o in result if o["a"] < val]
        if op == ">=":
            result = [o for o in result if o["a"] >= val]
        if op == "<=":
            result = [o for o in result if o["a"] <= val]
    found = list(sorted(found, key=lambda o: o["a"]))
    result = list(sorted(result, key=lambda o: o["a"]))
    assert found == result
