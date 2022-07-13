from dataclasses import dataclass
from typing import Optional

import unittest

from hashindex import HashIndex, FrozenHashIndex
from hashindex.utils import get_attributes
from hashindex.exceptions import FrozenError, ImmutableUpdateError


@dataclass
class Pokemon:
    name: str
    type1: str
    type2: Optional[str]

    def __repr__(self):
        if self.type2 is None:
            return f"{self.name}: {self.type1}"
        return f"{self.name}: {self.type1}/{self.type2}"


def make_test_data(index_type):
    zapdos = Pokemon("Zapdos", "Electric", "Flying")
    pikachu_1 = Pokemon("Pikachu", "Electric", None)
    pikachu_2 = Pokemon("Pikachu", "Electric", None)
    eevee = Pokemon("Eevee", "Normal", None)
    mi = index_type([zapdos, pikachu_1, pikachu_2, eevee], on=get_attributes(Pokemon))
    return mi


def test_find_one(index_type):
    mi = make_test_data(index_type)
    result = mi.find({"name": ["Zapdos"]})
    assert len(result) == 1


def test_find_match(index_type):
    mi = make_test_data(index_type)
    result = mi.find({"name": ["Pikachu", "Eevee"]})
    assert len(result) == 3


def test_find_excluding(index_type):
    mi = make_test_data(index_type)
    result = mi.find(
        match=None, exclude={"type2": None}
    )  # Zapdos is the only one with a type2
    assert len(result) == 1
    assert result[0].name == "Zapdos"


def test_another(index_type):
    mi = make_test_data(index_type)
    result = mi.find(
        match={"name": ["Pikachu", "Zapdos"], "type1": "Electric"},
        exclude={"type2": "Flying"},
    )
    assert len(result) == 2
    assert result[0].name == "Pikachu"
    assert result[1].name == "Pikachu"


class TestMutations(unittest.TestCase):

    def test_remove(self):
        for index_type in [HashIndex, FrozenHashIndex]:
            mi = make_test_data(index_type)
            two_chus = mi.find({"name": "Pikachu"})
            assert len(two_chus) == 2
            if index_type == FrozenHashIndex:
                with self.assertRaises(FrozenError):
                    mi.remove(two_chus[1])
            else:
                mi.remove(two_chus[1])
                one_chu = mi.find({"name": "Pikachu"})
                assert len(one_chu) == 1

    def test_update(self):
        for index_type in [HashIndex, FrozenHashIndex]:
            mi = make_test_data(index_type)
            eevee = mi.find({"name": "Eevee"})[0]
            update = {"name": "Glaceon", "type1": "Ice", "type2": None}
            if index_type == FrozenHashIndex:
                with self.assertRaises(FrozenError):
                    mi.update(eevee, update)
            else:
                mi.update(eevee, update)
                res_eevee = mi.find({"name": "Eevee"})
                res_glaceon = mi.find({"name": "Glaceon"})
                assert not res_eevee
                assert res_glaceon

    def test_add_frozen(self):
        for index_type in [HashIndex, FrozenHashIndex]:
            mi = make_test_data(index_type)
            glaceon = Pokemon("Glaceon", "Ice", None)
            if index_type == FrozenHashIndex:
                with self.assertRaises(FrozenError):
                    mi.add(glaceon)
            else:
                mi.add(glaceon)
                res = mi.find({"name": "Glaceon"})
                assert res == [glaceon]

    def test_update_immutable_object(self):
        x = 'blah'
        hi = HashIndex([x], [len])
        with self.assertRaises(ImmutableUpdateError):
            hi.update(x, {})
