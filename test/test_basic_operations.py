from dataclasses import dataclass
from typing import Optional

import unittest
import pytest

from hashindex import HashIndex, FrozenHashIndex
from hashindex.utils import get_attributes
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


def make_test_data(index_type):
    zapdos = Pokemon("Zapdos", "Electric", "Flying")
    pikachu_1 = Pokemon("Pikachu", "Electric", None)
    pikachu_2 = Pokemon("Pikachu", "Electric", None)
    eevee = Pokemon("Eevee", "Normal", None)
    hi = index_type([zapdos, pikachu_1, pikachu_2, eevee], on=get_attributes(Pokemon))
    return hi


def test_find_one(index_type):
    hi = make_test_data(index_type)
    result = hi.find({"name": ["Zapdos"]})
    assert len(result) == 1


def test_find_match(index_type):
    hi = make_test_data(index_type)
    result = hi.find({"name": ["Pikachu", "Eevee"]})
    assert len(result) == 3


def test_find_exclude_only(index_type):
    hi = make_test_data(index_type)
    result = hi.find(exclude={"type2": None})  # Zapdos is the only one with a type2
    assert len(result) == 1
    assert result[0].name == "Zapdos"


def test_two_fields(index_type):
    hi = make_test_data(index_type)
    result = hi.find(
        match={"name": ["Pikachu", "Zapdos"], "type1": "Electric"},
        exclude={"type2": "Flying"},
    )
    assert len(result) == 2
    assert result[0].name == "Pikachu"
    assert result[1].name == "Pikachu"


def test_three_fields(index_type):
    hi = make_test_data(index_type)
    result = hi.find(
        match={"name": ["Pikachu", "Zapdos"], "type1": "Electric", "type2": "Flying"}
    )
    assert len(result) == 1
    assert result[0].name == "Zapdos"


def test_exclude_all(index_type):
    hi = make_test_data(index_type)
    result = hi.find(exclude={"type1": ["Electric", "Normal"]})
    assert len(result) == 0


def test_find_ids(index_type):
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    hi = index_type(data, ["a", "b"])
    result = hi.find_ids({"b": 4})
    res_id = next(iter(result))
    assert res_id == id(data[1])


def test_remove(index_type):
    hi = make_test_data(index_type)
    two_chus = hi.find({"name": "Pikachu"})
    assert len(two_chus) == 2
    if index_type == FrozenHashIndex:
        with AssertRaises(AttributeError):
            hi.remove(two_chus[1])
    else:
        hi.remove(two_chus[1])
        one_chu = hi.find({"name": "Pikachu"})
        assert len(one_chu) == 1


def test_add(index_type):
    hi = make_test_data(index_type)
    glaceon = Pokemon("Glaceon", "Ice", None)
    if index_type == FrozenHashIndex:
        with AssertRaises(AttributeError):
            hi.add(glaceon)
    else:
        hi.add(glaceon)
        res = hi.find({"name": "Glaceon"})
        assert res == [glaceon]
