"""
MutableAttrIndex contains a dict of set of object IDs.

Well, ok, it's a little more complicated than that. We don't always
use sets, because sets are REALLY inefficient for small collections.

Bytes per integer, by collection size

|              | 1     | 10   | 50   | 100  | 1000 | 10000  |
|--------------|-------|------|------|------|------|--------|
| Python tuple | 56.8  | 14.0 | 9.3  | 8.6  | 32.2 | 39.7   |
| Python set   | 235.6 | 82.1 | 46.0 | 84.5 | 57.2 | 84.6   |
| cykhash set  | 168.5 | 26.5 | 23.6 | 22.3 | 17.0 | 13.6   |
| numpy array  | 169.6 | 23.4 | 11.1 | 9.6  | 8.2  | 8.0    |

Those numbers were measured by examining process-level memory usage before and after
collections were created, so there's a little +/- there.
For example, a set containing a SINGLE INTEGER is actually 248 bytes.
248.
Bytes.
To store a single 8-byte integer.

Seriously, you can check it yourself.
```
from pympler.asizeof import asizeof
asizeof(set([1]))
# Yep, says 248. Yes, that's actually bytes and not bits.
```

Imagine if all our attribute values were unique, and we're storing a dict of millions of sets of size 1.
Ouch. Yeah, let's not do that. In fact, let's not use Python set() at all! We're only storing numbers, so a typed set
will be much more efficient. The cykhash sets are just perfect for this. They're about as fast as Python sets,
and around 1/4 the RAM.

For smaller collections, below 100 numbers, cykhash is a bit inefficient, so we use tuples there instead.
While they are immutable, it's not a big deal to discard a tuple of size 100 and make another one.

And for collections of size 1... we just store the number.

Using different collection sizes like this helps keep our memory usage from going too crazy.
A naive implementation would spend a gigabyte of RAM indexing a few million integers. While this
adds a bit of code complexity, it's a pretty great trade. Just gotta test it for each collection size, and we do.

For the FrozenHashBox, we use numpy arrays, because they're the best. As long as you don't need to add or remove
objects, anyway.
"""

from typing import Callable, Union, Dict, Any, Iterable, Optional

from cykhash import Int64Set

from hashbox.constants import TUPLE_SIZE_MAX, SET_SIZE_MIN
from hashbox.init_helpers import compute_mutable_dict
from hashbox.utils import get_attribute


class MutableAttrIndex:
    """
    Stores the possible values of this attribute in a collection of buckets.
    Several values may be allocated to the same bucket for space efficiency reasons.
    """

    def __init__(
        self,
        attr: Union[Callable, str],
        obj_map: Dict[int, Any],
        objs: Optional[Iterable[Any]] = None,
    ):
        self.attr = attr
        self.obj_map = obj_map
        if objs:
            self.d = compute_mutable_dict(objs, attr)
        else:
            self.d = dict()

    def get_obj_ids(self, val: Any) -> Int64Set:
        """Get the object IDs associated with this value as an Int64Set."""
        ids = self.d.get(val, Int64Set())
        if isinstance(ids, tuple):
            return Int64Set(ids)
        elif isinstance(ids, Int64Set):
            return ids
        else:
            return Int64Set([ids])

    def add(self, ptr: int, obj: Any):
        """Add an object if it has this attribute."""
        val, success = get_attribute(obj, self.attr)
        if not success:
            return
        if val in self.d:
            if isinstance(self.d[val], tuple):
                if len(self.d[val]) == TUPLE_SIZE_MAX:
                    self.d[val] = Int64Set(self.d[val])
                    self.d[val].add(ptr)
                else:
                    self.d[val] = tuple(list(self.d[val]) + [ptr])
            elif isinstance(self.d[val], Int64Set):
                self.d[val].add(ptr)
            else:
                self.d[val] = (self.d[val], ptr)
        else:
            self.d[val] = ptr

    def remove(self, ptr: int, obj: Any):
        """Remove a single object from the index. ptr is already known to be in the index."""
        val, success = get_attribute(obj, self.attr)
        if not success:
            return
        obj_ids = self.d[val]
        if isinstance(obj_ids, tuple) or isinstance(obj_ids, Int64Set):
            if isinstance(obj_ids, tuple):
                self.d[val] = tuple(obj_id for obj_id in obj_ids if obj_id != ptr)
                if len(self.d[val]) == 1:
                    self.d[val] = self.d[val][0]
            else:
                self.d[val].remove(ptr)
                if len(self.d[val]) < SET_SIZE_MIN:
                    self.d[val] = tuple(self.d[val])
        else:
            del self.d[val]

    def get_all_ids(self):
        """Get the ID of every object that has this attribute.
        Called when matching or excluding {attr: hashindex.ANY}."""
        obj_ids = Int64Set()
        for key, val in self.d.items():
            if isinstance(val, tuple):
                obj_ids = obj_ids.union(Int64Set(val))
            elif isinstance(val, Int64Set):
                obj_ids = obj_ids.union(val)
            else:
                obj_ids.add(val)
        return obj_ids

    def get_values(self):
        """Get unique values we have objects for."""
        return set(self.d.keys())

    def __len__(self):
        tot = 0
        for key, val in self.d.items():
            if isinstance(val, tuple) or isinstance(val, Int64Set):
                tot += len(val)
            else:
                tot += 1
        return tot
