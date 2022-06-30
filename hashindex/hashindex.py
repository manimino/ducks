from typing import Iterable, Optional, List, Any, Dict, Set

from hashindex.exceptions import MissingIndexError, FrozenError
from hashindex.mutable import MutableIndex
from hashindex.frozen import FrozenIndex


class HashIndex:
    def __init__(self, fields: Iterable[str]):
        self.index = MutableIndex(fields)
        self.frozen = False

    def find(
        self,
        match: Optional[Dict[str, Any]] = None,
        exclude: Optional[Dict[str, Any]] = None,
    ) -> List:
        """
        Find objects that fit the query.

        Example: find(match={'color': ['red', 'green'], size='big'}, exclude={'shape': 'round') will return objects
        with color ('red' OR 'green') AND that are size 'big' AND NOT round.

        If the "match" term is None, all objects in the index will be matched.
        """
        return self.index.find(match, exclude)

    def add(self, obj):
        """Add object to collection, update indices."""
        if self.frozen:
            raise FrozenError("Cannot add item - index is frozen.")
        self.index.add(obj)

    def remove(self, obj):
        """Delete object and update indices."""
        if self.frozen:
            raise FrozenError("Cannot remove item - index is frozen.")
        self.index.remove(obj)

    def update(self, obj, new_values: dict):
        """
        Update the HashIndex for a changed object. Also applies the update to the object.

        new_values contains {field: new_value} for each changed field.
        """
        if self.frozen:
            raise FrozenError("Cannot update item - index is frozen.")
        self.index.update(obj, new_values)

    def find_ids(
        self,
        match: Optional[Dict[str, Any]] = None,
        exclude: Optional[Dict[str, Any]] = None,
    ) -> Set:
        return self.index.find_ids(match, exclude)

    def freeze(self):
        """
        Prevent future changes to the index. Makes find() faster. Reduces RAM usage.

        Any attempts to add / update / remove from a frozen index will throw exceptions.
        Call this method before using HashIndex in a multithreaded environment.

        There is no unlock(), just make a new index if you want that. To make a new index, you can do:
        new_index = HashIndex(this_index.fields)
        for obj in this_index:
            new_index.add(obj)
        """
        if self.frozen:
            return
        self.frozen = True
        self.index = FrozenIndex(self.index)

    def values_of(self, field) -> Iterable:
        """Get available values for a given field."""
        if field not in self.indices:
            raise MissingIndexError
        return self.indices[field].keys()

    def __contains__(self, item):
        return item in self.index

    def __iter__(self):
        return iter(self.index)


def get_attributes(cls) -> List[str]:
    """Helper function to grab the attributes of a class"""
    return list(cls.__annotations__.keys())
