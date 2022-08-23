# Design ideas

This is just a place to note things that could be implemented in future.

### BTree indexing

The weak point of dbox at present is high-cardinality data, such as numerics. Those don't go well in the 
hash-based data structures.

But that could be pretty easily improved. 

#### DBox implementation

The `BTrees` package contains an `OLBTree` that would work well. 

When a maximum cardinality was reached, say 10k, an attempt would be made to create an OLBTree. 
It could fail due to mismatched object types. Is `(1, 2) > 'bees'`? That will throw a `TypeError`, and we'd know
that no BTree could be created.

Otherwise, with attribute values as the keys and object IDs as the values, an `OLBTree` should be fine.
It supports range queries directly - [you can call values(min, max) and get the value for a key range](https://btrees.readthedocs.io/en/stable/api.html#BTrees.Interfaces.IMinimalDictionary.values).
So it would work perfectly.

The build time is around 1s / million items, so it's viable there. The RAM usage was something like 70 bytes / object
which is doable too. Especially if we could remove the hashtable in the process. Might be a different subclass type.

#### FrozenDBox implementation

Creating a range query thing in numpy:
 - Attempt to sort the values array with `argsort`
 - If that works, sort the values and the indexes by the values.
 - Query does `bisect_left()` and `bisect_right()` to get the range of indexes for a `<` / `>` query.

A thought: Is this generally better than what we have? It seems like creating the hash-based arrays
is more difficult, and while it's versatile, it may not be buying us much. We have to bisect anyway when
locating a hash of a value; bisecting on the value itself should be as fast or faster. Assuming the objects
are comparable, of course.

### Default order

It may be smarter to "assume BTree" at first, and fail over to hash only if needed due to a type conflict. 
Most situations are going to have objects that are efficiently comparable.
