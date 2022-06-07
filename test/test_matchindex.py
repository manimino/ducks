from dataclasses import dataclass
from typing import Optional

from matchindex import MatchIndex, get_attributes


@dataclass
class Pokemon:
    name: str
    type1: str
    type2: Optional[str]

    def __repr__(self):
        if self.type2 is None:
            return f"{self.name}: {self.type1}"
        return f"{self.name}: {self.type1}/{self.type2}"


def make_test_data():
    zapdos = Pokemon('Zapdos', 'Electric', 'Flying')
    pikachu_1 = Pokemon('Pikachu', 'Electric', None)
    pikachu_2 = Pokemon('Pikachu', 'Electric', None)
    eevee = Pokemon('Eevee', 'Normal', None)
    mi = MatchIndex(get_attributes(Pokemon))
    mi.add(zapdos)
    mi.add(pikachu_1)
    mi.add(pikachu_2)
    mi.add(eevee)
    return mi


def test_delete():
    mi = make_test_data()
    two_chus = mi.find({'name': 'Pikachu'})
    assert len(two_chus) == 2
    mi.remove(two_chus[1])
    one_chu = mi.find({'name': 'Pikachu'})
    assert len(one_chu) == 1


def test_update():
    mi = make_test_data()
    eevee = mi.find({'name': 'Eevee'})[0]
    mi.update(eevee, {'name': 'Jolteon', 'type1': 'Electric', 'type2': None})
    res_eevee = mi.find({'name': 'Eevee'})
    res_jolteon = mi.find({'name': 'Jolteon'})
    assert not res_eevee
    assert res_jolteon


def test_excluding():
    mi = make_test_data()
    result = mi.find(match=None, exclude={'type2': None})  # Zapdos is the only one with a type2
    assert len(result) == 1
    assert result[0].name == 'Zapdos'


def test_union():
    mi = make_test_data()
    result = mi.find({'name': ['Pikachu', 'Eevee']})
    assert len(result) == 3
