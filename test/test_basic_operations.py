from dataclasses import dataclass
from typing import Optional

from filtered import FrozenFiltered
from filtered.utils import get_attributes
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


def make_test_data(index_type):
    zapdos = Pokemon("Zapdos", "Electric", "Flying")
    pikachu_1 = Pokemon("Pikachu", "Electric", None)
    pikachu_2 = Pokemon("Pikachu", "Electric", None)
    eevee = Pokemon("Eevee", "Normal", None)
    f = index_type([zapdos, pikachu_1, pikachu_2, eevee], on=get_attributes(Pokemon))
    return f


def test_find_one(index_type):
    f = make_test_data(index_type)
    result = f.find({"name": ["Zapdos"]})
    assert len(result) == 1


def test_find_union(index_type):
    f = make_test_data(index_type)
    result = f.find({"name": ["Pikachu", "Eevee"]})
    assert len(result) == 3


def test_find_union_with_mismatch(index_type):
    f = make_test_data(index_type)
    result = f.find({"name": ["Pikachu", "Shykadu"]})
    assert len(result) == 2


def test_find_list_of_one(index_type):
    f = make_test_data(index_type)
    result = f.find({"name": ["Pikachu"]})
    assert len(result) == 2


def test_find_sub_obj(index_type):
    objs = [
        {"p": Pokemon("Zapdos", "Electric", "Flying")},
        {"p": Pokemon("Pikachu", "Electric", None)},
    ]
    f = index_type(objs, on=["p"])
    found = f.find()
    found_empty = f.find({}, {})
    assert len(found) == 2
    assert len(found_empty) == 2
    for obj in objs:
        assert obj in found
        assert obj in found_empty


def test_find_exclude_only(index_type):
    f = make_test_data(index_type)
    result = f.find(exclude={"type2": None})  # Zapdos is the only one with a type2
    assert len(result) == 1
    assert result[0].name == "Zapdos"


def test_two_fields(index_type):
    f = make_test_data(index_type)
    result = f.find(
        match={"name": ["Pikachu", "Zapdos"], "type1": "Electric"},
        exclude={"type2": "Flying"},
    )
    assert len(result) == 2
    assert result[0].name == "Pikachu"
    assert result[1].name == "Pikachu"


def test_three_fields(index_type):
    f = make_test_data(index_type)
    result = f.find(
        match={"name": ["Pikachu", "Zapdos"], "type1": "Electric", "type2": "Flying"}
    )
    assert len(result) == 1
    assert result[0].name == "Zapdos"


def test_exclude_all(index_type):
    f = make_test_data(index_type)
    result = f.find(exclude={"type1": ["Electric", "Normal"]})
    assert len(result) == 0


def test_remove(index_type):
    f = make_test_data(index_type)
    two_chus = f.find({"name": "Pikachu"})
    assert len(two_chus) == 2
    if index_type == FrozenFiltered:
        with AssertRaises(AttributeError):
            f.remove(two_chus[1])
    else:
        f.remove(two_chus[1])
        one_chu = f.find({"name": "Pikachu"})
        assert len(one_chu) == 1


def test_add(index_type):
    f = make_test_data(index_type)
    glaceon = Pokemon("Glaceon", "Ice", None)
    if index_type == FrozenFiltered:
        with AssertRaises(AttributeError):
            f.add(glaceon)
    else:
        f.add(glaceon)
        res = f.find({"name": "Glaceon"})
        assert res == [glaceon]
