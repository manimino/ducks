from collections import deque
from dataclasses import dataclass
from typing import Iterable, Optional, List, Any, Dict


class MissingIndexError(Exception):
    """Raised when querying a field we don't have an index for"""
    pass


class MissingValueError(Exception):
    """Raised when adding an object that is missing a field we need to index"""
    pass


class MissingObjectError(Exception):
    """Raised when removing or updating an object we don't have."""
    pass


def get_attribs(cls):
    """Helper function to grab the attributes of a class"""
    return list(cls.__annotations__.keys())

class HashBox:
    def __init__(self, fields: Iterable[str]):
        # the objects themselves are stored in a dict of {pointer: obj}
        self.objs = dict()

        # Make an index for each field.
        # Each index is a dict of {field_value: set(pointers)}.
        self.indices = {}
        for field in fields:
            self.indices[field] = dict()

    def add(self, obj):
        """Add object to collection, update indices."""
        self.objs[id(obj)] = obj

        # update indices
        for field in self.indices:
            val = obj.__dict__[field]
            idx = self.indices[field]
            if val not in idx:
                idx[val] = set()
            idx[val].add(id(obj))

    def values_of(self, field) -> Iterable:
        """Get available values for a given field."""
        if field not in self.indices:
            raise MissingIndexError
        return self.indices[field].keys()

    def find(self, having: Optional[Dict[str, Any]] = None, excluding: Optional[Dict[str, Any]] = None) -> List:
        """
        Perform lookup based on given values.

        If "having" is None / empty, it matches all objects.
        There is an implicit "AND" joining all constraints.
        """
        # check that we have an index for all desired lookups
        required_indices = set()
        if having:
            required_indices.update(having.keys())
        if excluding:
            required_indices.update(excluding.keys())
        missing_indices = required_indices.difference(self.indices)
        if missing_indices:
            raise MissingIndexError

        hits = None
        if having:
            # result is the intersection of all query items
            for field, value in having.items():
                field_hits = self.indices[field][value]
                if hits is None:
                    hits = field_hits
                else:
                    hits = set.intersection(hits, field_hits)
        else:
            hits = set(self.objs.keys())

        if excluding:
            for field, value in excluding.items():
                field_hits = self.indices[field][value]
                hits = set.difference(hits, field_hits)

        return [self.objs[ptr] for ptr in hits]

    def remove(self, obj):
        """Delete object and update indices."""
        ptr = id(obj)
        if ptr not in self.objs:
            raise MissingObjectError

        for field in self.indices:
            val = obj.__dict__[field]
            idx = self.indices[field]
            idx[val].remove(ptr)
            if not idx[val]:
                del idx[val]
        del self.objs[ptr]

    def update(self, obj, changes: dict):
        """Update fields of an existing object"""
        ptr = id(obj)
        if ptr not in self.objs:
            raise MissingObjectError
        for field, new_value in changes.items():
            # update obj
            old_value = obj.__dict__[field]
            obj.__dict__[field] = new_value
            # update index
            if field in self.indices:
                idx = self.indices[field]
                idx[old_value].remove(ptr)
                if not idx[old_value]:
                    del idx[old_value]

                if new_value not in idx:
                    idx[new_value] = set()
                idx[new_value].add(ptr)


# Test usage

@dataclass
class Pokemon:
    name: str
    type1: str
    type2: str
    hp: int
    hp_max: int

    def __repr__(self):
        if self.type2 is None:
            return f"{self.name}, {self.type1}, HP:{self.hp}/{self.hp_max}"
        return f"{self.name}, {self.type1}/{self.type2}, HP:{self.hp}/{self.hp_max}"


def main():
    pokemon = [
        Pokemon(name='Jigglypuff', type1='Normal', type2=None, hp=150, hp_max=150),
        Pokemon(name='Bulbasaur', type1='Grass', type2=None, hp=100, hp_max=100),
        Pokemon(name='Ivysaur', type1='Grass', type2=None, hp=200, hp_max=200),
        Pokemon(name='Venusaur', type1='Grass', type2=None, hp=300, hp_max=300),
        Pokemon(name='Zapdos', type1='Flying', type2='Electric', hp=1000, hp_max=1000),
        Pokemon(name='Pikachu', type1='Electric', type2=None, hp=1000, hp_max=1000),
    ]
    attribs = Pokemon.__annotations__.keys()
    box = IndexedObjects(attribs)
    for p in pokemon:
        box.add(p)
    box.remove(pokemon[1])
    box.update(pokemon[2], {'hp': 500})
    print(box.find())
    print(box.find(having={'type2': None}))
    print(box.find(excluding={'type2': None}))

    bidoof = Pokemon(name='Bidoof', type1='Electric', type2=None, hp=111, hp_max=111)
    box.update(pokemon[-1],)


if __name__ == '__main__':
    main()
