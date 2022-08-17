from BTrees.OOBTree import OOBTree

from typing import List, Dict, Any, Tuple


class BTree:
    """
    Wraps an OOBTree instance. Not subclassing because we only need a few methods.
     - BTrees len() does a full tree traversal, which is very slow. So we maintain a count instead.
     - BTrees stores None values as if they were just really really small. So "x < 1" will find the Nones.
     Let's disallow None entirely, make it throw TypeError. Just like sorting [1, 2, None] would do.
     - BTrees values(min_key, max_key) does an inclusive range [min_key, max_key]. But often you need one or both
     sides to exclude the endpoints, so that's implemented here.
     - Provides a nice interface for using >, >=, <, <= to get value ranges.
    """

    def __init__(self, d: Dict[Any, Any] = None):
        if d:
            if None in d:
                raise TypeError(
                    "None is not allowed in BTree because it breaks comparisons."
                )
            self.tree = OOBTree(d)
            self.length = len(d)
        else:
            self.tree = OOBTree()
            self.length = 0

    def get_range_expr(self, expr: Dict[str, Any]) -> List:
        min_key, max_key, include_min, include_max = range_expr_to_args(expr)
        return self.get_range(min_key, max_key, include_min, include_max)

    def get_range(
        self,
        min_key=None,
        max_key=None,
        include_min: bool = True,
        include_max: bool = True,
    ) -> List:
        """
        Get values in the range of [min_key, max_key]. include_min and include_max
        determine whether values for the start and end keys will be included.

        Examples:
            Get all values: None, None, True, True
            Get 1 < key < 10: 1, 10, False, False
            Get key >= 3: 3, None, True, True
        """
        if len(self) == 0:
            return []
        if include_min and include_max:
            return self.tree.values(min_key, max_key)

        # get keys between min and max (inclusive) and apply min / max inequality constraints
        keys = self.tree.keys(min_key, max_key)
        if len(keys) == 0:
            return []
        left = 0
        right = len(keys) - 1

        # move left pointer up if it's on min_key and we're not doing include_min
        if not include_min and keys[left] == min_key:
            left += 1
        if left == len(keys) or left > right:
            return []

        # move right pointer down if it's on max_key and we're not doing include_max
        if not include_max and keys[right] == max_key:
            right -= 1
        if right < left:
            return []
        return self.tree.values(keys[left], keys[right])

    def get(self, key, default=None):
        return self.tree.get(key, default)

    def keys(self):
        return self.tree.keys()

    def values(self):
        return self.tree.values()

    def items(self):
        return self.tree.items()

    def __len__(self):
        return self.length

    def __setitem__(self, key, value):
        if key is None:
            raise TypeError(
                "None is not allowed in BTree because it breaks comparisons."
            )
        if len(self) == 0:
            # OOBTree oddity: it allows a non-comparable object on the first insert, but
            # if it gets one, all future inserts will fail.
            # So let's raise a TypeError if the very first insert is a non-comparable type.
            key > key
        if key not in self.tree:
            self.length += 1
        self.tree[key] = value

    def __getitem__(self, key):
        return self.tree[key]

    def __delitem__(self, key):
        self.length -= 1
        del self.tree[key]

    def __contains__(self, item):
        return item in self.tree


def range_expr_to_args(expr: Dict[str, Any]) -> Tuple[Any, Any, bool, bool]:
    """
    Turn a range expr into (min_key, max_key, include_min, include_max), which are easier to use with BTrees.
    e.g., translates {'<': 3} into get_values(3, None, True, False).
    Will ignore keys in expr other than '<', '<=', '>', '>='.
    """
    min_key = None
    max_key = None
    include_min = True
    include_max = True
    if ">" in expr:
        min_key = expr[">"]
        include_min = False
    if ">=" in expr:
        min_key = expr[">="]
        include_min = True
    if "<" in expr:
        max_key = expr["<"]
        include_max = False
    if "<=" in expr:
        max_key = expr["<="]
        include_max = True
    return min_key, max_key, include_min, include_max
