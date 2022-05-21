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


class MatchIndex:
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

    def _matches_for(self, field: str, value: Any):
        """Get matches during a find(). Helper function to handle union-on-list logic."""
        if type(value) is list:
            # take the union of all matches
            matches = set()
            for v in value:
                v_matches = self.indices[field].get(v, set())
                matches = set.union(matches, v_matches)
            return matches
        else:
            return self.indices[field].get(value, set())

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
                field_hits = self._matches_for(field, value)
                if hits is None:
                    hits = field_hits
                if not field_hits:
                    break
                else:
                    hits = set.intersection(hits, field_hits)
        else:
            hits = set(self.objs.keys())

        if excluding:
            for field, value in excluding.items():
                field_hits = self._matches_for(field, value)
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

    def __repr__(self):
        if self.type2 is None:
            return f"{self.name}: {self.type1}"
        return f"{self.name}: {self.type1}/{self.type2}"


def main():
    zapdos = Pokemon('Zapdos', 'Electric', 'Flying')
    pikachu_1 = Pokemon('Pikachu', 'Electric', None)
    pikachu_2 = Pokemon('Pikachu', 'Electric', None)
    eevee = Pokemon('Eevee', 'Normal', None)

    mi = MatchIndex(get_attribs(Pokemon))
    mi.add(zapdos)
    mi.add(pikachu_1)
    mi.add(pikachu_2)
    mi.add(eevee)

    result = mi.find(having={'name': 'Pikachu'})  # Finds two Pikachus
    print('2 Pikachus:', result)

    mi.remove(pikachu_2)
    result = mi.find(having={'name': 'Pikachu'})  # Finds one Pikachu
    print('1 Pikachu:', result)

    result = mi.find(having=None, excluding={'type2': None})  # Finds Zapdos
    print('Zapdos:', result)

    result = mi.find({'type1': ['Electric', 'Normal']})  # Finds everything
    print('everything', result)

    mi.update(eevee, {'name': 'Jolteon', 'type1': 'Electric', 'type2': None})
    result = mi.find({'name': 'Eevee'})    # No results
    print('empty:', result)

    result = mi.find({'name': 'Jolteon'})  # Finds Jolteon
    print('Jolteon', result)

if __name__ == '__main__':
    main()
