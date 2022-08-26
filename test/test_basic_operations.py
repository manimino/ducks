from dataclasses import dataclass
from typing import Optional, Union

import pytest

from ducks import Dex, FrozenDex
from ducks.utils import get_attributes
from .conftest import AssertRaises


@dataclass
class Pokemon:
    name: str
    type1: str
    type2: Optional[str]

    def __repr__(self):
        if self.type2 is None:
            return f"{self.name}: {self.type1}"
        return f"{self.name}: {self.type1}/{self.type2}"

    def __hash__(self):
        t = (self.name, self.type1, self.type2)
        return hash(t)

    def __lt__(self, other):
        return self.name < other.name


def make_test_ducks(box_class) -> Union[Dex, FrozenDex]:
    zapdos = Pokemon("Zapdos", "Electric", "Flying")
    pikachu_1 = Pokemon("Pikachu", "Electric", None)
    pikachu_2 = Pokemon("Pikachu", "Electric", None)
    eevee = Pokemon("Eevee", "Normal", None)
    f = box_class([zapdos, pikachu_1, pikachu_2, eevee], on=get_attributes(Pokemon))
    return f


def test_find_one(box_class):
    f = make_test_ducks(box_class)
    result = f[{"name": "Zapdos"}]
    assert len(result) == 1


def test_find_union(box_class):
    f = make_test_ducks(box_class)
    result = f[{"name": ["Pikachu", "Eevee"]}]
    assert len(result) == 3


def test_find_union_with_mismatch(box_class):
    f = make_test_ducks(box_class)
    result = f[{"name": ["Pikachu", "Shykadu"]}]
    assert len(result) == 2


def test_find_in_iterable_of_one(box_class):
    f = make_test_ducks(box_class)
    result = f[{"name": {"in": {"Pikachu"}}}]
    assert len(result) == 2


@pytest.mark.parametrize(
    "expr, expected_len",
    [
        ({">": "Yapdos"}, 1),
        ({">=": "Yapdos"}, 1),
        ({">": "AAA", "<": "zzz"}, 4),
        ({">=": "Eevee", "<": "Pikachu"}, 1),
        ({">=": "Eevee", "<=": "Pikachu"}, 3),
        ({"ge": "Eevee", "le": "Pikachu"}, 3),
        ({">": "Eevee", "<": "Zapdos"}, 2),
        ({"gt": "Eevee", "lt": "Zapdos"}, 2),
        ({"<": "Eevee"}, 0),
        ({"<": "Eevee", ">": "Zapdos"}, 0),
    ],
)
def test_find_greater_less(box_class, expr, expected_len):
    f = make_test_ducks(box_class)
    result = f[{"name": expr}]
    assert len(result) == expected_len


def test_find_sub_obj(box_class):
    objs = [
        {"p": Pokemon("Zapdos", "Electric", "Flying")},
        {"p": Pokemon("Pikachu", "Electric", None)},
    ]
    f = box_class(objs, on=["p"])
    found_empty = f[{}]
    assert len(found_empty) == 2
    for obj in objs:
        assert obj in found_empty


def test_find_exclude_only(box_class):
    f = make_test_ducks(box_class)
    result = f[{"type2": {"!=": None}}]  # Zapdos is the only one with a type2
    assert len(result) == 1
    assert result[0].name == "Zapdos"


def test_two_attrs(box_class):
    f = make_test_ducks(box_class)
    result = f[
        {
            "name": {"in": ["Pikachu", "Zapdos"]},
            "type1": "Electric",
            "type2": {"!=": "Flying"},
        }
    ]
    assert len(result) == 2
    assert result[0].name == "Pikachu"
    assert result[1].name == "Pikachu"


def test_three_attrs(box_class):
    f = make_test_ducks(box_class)
    result = f[
        {"name": {"in": ["Pikachu", "Zapdos"]}, "type1": "Electric", "type2": "Flying",}
    ]
    assert len(result) == 1
    assert result[0].name == "Zapdos"


def test_exclude_all(box_class):
    f = make_test_ducks(box_class)
    result = f[{"type1": {"not in": ["Electric", "Normal"]}}]
    assert len(result) == 0


def test_remove(box_class):
    f = make_test_ducks(box_class)
    two_chus = f[{"name": "Pikachu"}]
    assert len(two_chus) == 2
    if box_class == FrozenDex:
        with AssertRaises(AttributeError):
            f.remove(two_chus[1])
    else:
        f.remove(two_chus[1])
        one_chu = f[{"name": "Pikachu"}]
        assert len(one_chu) == 1


def test_add(box_class):
    f = make_test_ducks(box_class)
    glaceon = Pokemon("Glaceon", "Ice", None)
    if box_class == FrozenDex:
        with AssertRaises(AttributeError):
            f.add(glaceon)
    else:
        f.add(glaceon)
        res = f[{"name": "Glaceon"}]
        assert res == [glaceon]


def test_multi_exclude(box_class):
    fb = make_test_ducks(box_class)
    res = fb[{"name": {"!=": "Pikachu"}, "type1": {"not in": ["Normal"]}}]
    zapdos_ls = [p for p in fb if p.name == "Zapdos"]
    assert res == zapdos_ls


def test_get_values(box_class):
    fb = make_test_ducks(box_class)
    assert fb.get_values("name") == {"Zapdos", "Pikachu", "Eevee"}
    assert fb.get_values("type1") == {"Electric", "Normal"}
    assert fb.get_values("type2") == {"Flying", None}
