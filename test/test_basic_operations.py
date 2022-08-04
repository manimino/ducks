from dataclasses import dataclass
from typing import Optional, Union

from hashbox import HashBox, FrozenHashBox
from hashbox.utils import get_attributes
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


def make_test_hashbox(box_class) -> Union[HashBox, FrozenHashBox]:
    zapdos = Pokemon("Zapdos", "Electric", "Flying")
    pikachu_1 = Pokemon("Pikachu", "Electric", None)
    pikachu_2 = Pokemon("Pikachu", "Electric", None)
    eevee = Pokemon("Eevee", "Normal", None)
    f = box_class([zapdos, pikachu_1, pikachu_2, eevee], on=get_attributes(Pokemon))
    return f


def test_find_one(box_class):
    f = make_test_hashbox(box_class)
    result = f.find({"name": ["Zapdos"]})
    assert len(result) == 1


def test_find_union(box_class):
    f = make_test_hashbox(box_class)
    result = f.find({"name": ["Pikachu", "Eevee"]})
    assert len(result) == 3


def test_find_union_with_mismatch(box_class):
    f = make_test_hashbox(box_class)
    result = f.find({"name": ["Pikachu", "Shykadu"]})
    assert len(result) == 2


def test_find_list_of_one(box_class):
    f = make_test_hashbox(box_class)
    result = f.find({"name": ["Pikachu"]})
    assert len(result) == 2


def test_find_sub_obj(box_class):
    objs = [
        {"p": Pokemon("Zapdos", "Electric", "Flying")},
        {"p": Pokemon("Pikachu", "Electric", None)},
    ]
    f = box_class(objs, on=["p"])
    found = f.find()
    found_empty = f.find({}, {})
    assert len(found) == 2
    assert len(found_empty) == 2
    for obj in objs:
        assert obj in found
        assert obj in found_empty


def test_find_exclude_only(box_class):
    f = make_test_hashbox(box_class)
    result = f.find(exclude={"type2": None})  # Zapdos is the only one with a type2
    assert len(result) == 1
    assert result[0].name == "Zapdos"


def test_two_attrs(box_class):
    f = make_test_hashbox(box_class)
    result = f.find(
        match={"name": ["Pikachu", "Zapdos"], "type1": "Electric"},
        exclude={"type2": "Flying"},
    )
    assert len(result) == 2
    assert result[0].name == "Pikachu"
    assert result[1].name == "Pikachu"


def test_three_attrs(box_class):
    f = make_test_hashbox(box_class)
    result = f.find(
        match={"name": ["Pikachu", "Zapdos"], "type1": "Electric", "type2": "Flying"}
    )
    assert len(result) == 1
    assert result[0].name == "Zapdos"


def test_exclude_all(box_class):
    f = make_test_hashbox(box_class)
    result = f.find(exclude={"type1": ["Electric", "Normal"]})
    assert len(result) == 0


def test_remove(box_class):
    f = make_test_hashbox(box_class)
    two_chus = f.find({"name": "Pikachu"})
    assert len(two_chus) == 2
    if box_class == FrozenHashBox:
        with AssertRaises(AttributeError):
            f.remove(two_chus[1])
    else:
        f.remove(two_chus[1])
        one_chu = f.find({"name": "Pikachu"})
        assert len(one_chu) == 1


def test_add(box_class):
    f = make_test_hashbox(box_class)
    glaceon = Pokemon("Glaceon", "Ice", None)
    if box_class == FrozenHashBox:
        with AssertRaises(AttributeError):
            f.add(glaceon)
    else:
        f.add(glaceon)
        res = f.find({"name": "Glaceon"})
        assert res == [glaceon]


def test_multi_exclude(box_class):
    hb = make_test_hashbox(box_class)
    res = hb.find(exclude={"name": "Pikachu", "type1": ["Normal"]})
    zapdos_ls = [p for p in hb if p.name == "Zapdos"]
    assert res == zapdos_ls


def test_get_values(box_class):
    hb = make_test_hashbox(box_class)
    assert hb.get_values('name') == {'Zapdos', 'Pikachu', 'Eevee'}
    assert hb.get_values('type1') == {'Electric', 'Normal'}
    assert hb.get_values('type2') == {'Flying', None}
