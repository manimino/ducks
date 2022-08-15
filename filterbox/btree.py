"""
BTrees.OOBTree is great, it makes this project possible.
But look at that grade, it could be a little better! Let's bring it up to an A-.

Specifically addresses:
"""

from BTrees.OOBTree import OOBTree


class BTree():
    """
    Wraps an OOBTree instance. Not subclassing because we only use a few methods.
    Fixes two things about it that we need.
     - BTrees len() does a full tree traversal, which costs a lot of time. So we maintain a count.
     - BTrees values(min_key, max_key) does an inclusive range [min_key, max_key]. Often you need one or both
     sides to exclude the endpoints.
    """
    def __init__(self):
        self.tree = OOBTree()
        self.length = 0

    def get_values(self, min_key, max_key, include_min: bool, include_max: bool):
        pass

    def __len__(self):
        return self.length

    def __setitem__(self, key, value):
        if key not in self.tree:
            self.length += 1
        tree[key] = value

    def __delitem__(self, key):
