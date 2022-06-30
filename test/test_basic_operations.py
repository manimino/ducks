from dataclasses import dataclass
from typing import Optional

import unittest

from hashindex import HashIndex, get_attributes
from hashindex.exceptions import FrozenError

@dataclass
class Pokemon:
    name: str
    type1: str
    type2: Optional[str]

    def __repr__(self):
        if self.type2 is None:
            return f"{self.name}: {self.type1}"
        return f"{self.name}: {self.type1}/{self.type2}"


def make_test_data(freeze):
    zapdos = Pokemon("Zapdos", "Electric", "Flying")
    pikachu_1 = Pokemon("Pikachu", "Electric", None)
    pikachu_2 = Pokemon("Pikachu", "Electric", None)
    eevee = Pokemon("Eevee", "Normal", None)
    mi = HashIndex(get_attributes(Pokemon))
    mi.add(zapdos)
    mi.add(pikachu_1)
    mi.add(pikachu_2)
    mi.add(eevee)
    if freeze:
        mi.freeze()
    return mi


def test_find_one(freeze):
    mi = make_test_data(freeze)
    result = mi.find({"name": ["Zapdos"]})
    assert len(result) == 1


def test_find_match(freeze):
    mi = make_test_data(freeze)
    result = mi.find({"name": ["Pikachu", "Eevee"]})
    assert len(result) == 3


def test_find_excluding(freeze):
    mi = make_test_data(freeze)
    result = mi.find(
        match=None, exclude={"type2": None}
    )  # Zapdos is the only one with a type2
    assert len(result) == 1
    assert result[0].name == "Zapdos"


def test_another(freeze):
    mi = make_test_data(freeze)
    result = mi.find(
        match={"name": ["Pikachu", "Zapdos"], "type1": "Electric"},
        exclude={"type2": "Flying"},
    )
    assert len(result) == 2
    assert result[0].name == "Pikachu"
    assert result[1].name == "Pikachu"


class TestMutations(unittest.TestCase):

    def test_remove(self):
        for freeze in [False, True]:
            mi = make_test_data(freeze)
            two_chus = mi.find({"name": "Pikachu"})
            assert len(two_chus) == 2
            if freeze:
                with self.assertRaises(FrozenError):
                    mi.remove(two_chus[1])
            else:
                mi.remove(two_chus[1])
                one_chu = mi.find({"name": "Pikachu"})
                assert len(one_chu) == 1

    def test_update(self,):
        for freeze in [False, True]:
            mi = make_test_data(freeze)
            eevee = mi.find({"name": "Eevee"})[0]
            update = {"name": "Glaceon", "type1": "Ice", "type2": None}
            if freeze:
                with self.assertRaises(FrozenError):
                    mi.update(eevee, update)
            else:
                mi.update(eevee, update)
                res_eevee = mi.find({"name": "Eevee"})
                res_glaceon = mi.find({"name": "Glaceon"})
                assert not res_eevee
                assert res_glaceon

    def test_add_frozen(self):
        for freeze in [False, True]:
            mi = make_test_data(freeze)
            glaceon = Pokemon("Glaceon", "Ice", None)
            if freeze:
                with self.assertRaises(FrozenError):
                    mi.add(glaceon)
            else:
                mi.add(glaceon)
                res = mi.find({"name": "Glaceon"})
                assert res == [glaceon]
