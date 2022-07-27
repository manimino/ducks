# Data Structures

## Overview

 - Filtered [mutable.py](filtered/mutable.py)
    - MutableFieldIndex
      - HashBucket
      - DictBucket
 - FrozenFiltered
   - FrozenFieldIndex
     - FHashBucket
     - FDictBucket

### Filtered - main class

A Filtered object contains:
 - a list of MutableFieldIndex objects, one for each attribute
 - an id-to-object lookup dictionary

When a query comes in, Filtered asks each MutableFieldIndex for the IDs of objects that match the query values for its 
field. Each FieldIndex returns a collection of object IDs. 

Filtered then applies union, intersect, and difference operations on the object IDs to get a final set of object 
IDs. It looks up each object ID in its dictionary to get the objects, and returns them.

### MutableFieldIndex

A FieldIndex's goal is to store sets of object IDs for lookup by the hashed field value. (Note: 'Field' is a 
synonym for 'Attribute' throughout the code and documentation.)

Let's look at the best way to store sets of object IDs.

#### Bytes per integer, by collection size

|              | 1     | 10   | 50   | 100  | 1000 | 10000 |
|--------------|-------|------|------|------|------|-------|
| Python set   | 235.6 | 82.1 | 46.0 | 84.5 | 57.2 | 84.6  |
| cykhash set  | 168.5 | 26.5 | 23.6 | 22.3 | 17.0 | 13.6  |
| numpy array  | 169.6 | 23.4 | 11.1 | 9.6  | 8.2  | 8.0   |

- Python sets are quite expensive. We won't use those.
- A cykhash set is a typed set, of type Int64 in this case. Typed sets are much more memory-efficient than the generic 
Python sets. They are implemented by the [cykhash](https://github.com/realead/cykhash) library. 
- Numpy arrays, while very memory-efficient, can't be used in the MutableFieldIndex. We'll see those later in the
FrozenFiltered implementation.

For all three, there is a high overhead cost. Storing many collections of size 1 is a bad idea. Nearly-unique values
(high cardinality data) are very likely to be in datasets. We need a bucketing strategy to allow storage of similar
hashes in one larger collection. This common solution is also done in the 
[Postgres Filtered]([Postgres's Filtered](https://www.postgresql.org/docs/current/hash-implementation.html)),
for example.

Thus, a MutableFieldIndex contains:
 - A collection of HashBucket and DictBucket items. The collection is a SortedDict (B-tree); buckets are ordered based
on the range of value hashes they hold.
 - Logic for finding the appropriate bucket for a hashed value, splitting buckets, and deleting buckets.

[!Layout of DictBucket and HashBucket in a MutableFieldIndex](bucketing.png)

### HashBucket

A single bucket contains the object ids for a range of hashed values. On query, all object IDs in the bucket are 
considered as match candidates. The candidates are filtered by checking if their value matches the query.

A HashBucket is only allowed to contain up to a certain number of values; after that, it must be split or converted to
a DictBucket. 

Keeping the HashBuckets small improves lookup speed, but making them larger gives better memory efficiency.
Going by the table above, a size between 10 and 1000 is a reasonable maximum size.

### DictBucket

What happens when millions of objects have the same value? That would violate the maximum size of a HashBucket.
DictBucket covers this case.

Each DictBucket holds all object IDs that have a specific hashed value. Potentially, two or more values could have the 
same hash (a collision). Therefore, the DictBucket is a dict of {value: {object_id_set}} so distinct values are stored
separately even if they have the same hash.

### Summary / Performance

While this design is more complex than the naive dict-of-set implementation, the memory efficiency is tremendously 
improved. This allows Filtered to store far more items than it would otherwise.

DictBucket works pretty much the same as a dict-of-set does, with the minor overhead of needing to locate the bucket. 
So the lookup speed there is quite fast.

There's more of a performance hit when a query needs to find small keys. However, queries that find small keys
tend to be fast in other ways. Their intersect and union operations are trivial, and their object-id-to-object lookups
are quick thanks to the low number of objects. So the overall speed of a small query is still very fast.

____

### FrozenIndex

It's the same overall design as Filtered. The big difference is that it does not use sets. In place of a sets of object
IDs, FrozenIndex uses pairs of numpy arrays: one of objects, one of IDs. Both arrays are sorted by object ID.

Operations on sorted arrays are quite fast. Consider that lookup in a set is O(1), unless you get unlucky, and 
then it's up to O(n). A sorted array lookup is O(log n). Operations like intersection and union in
sorted arrays benefit from significant locality advantages as well. 

The major downside is mutability; adding or removing an element requires making a new array. But in a frozen
container, this is not a concern. Buckets and their arrays are intelligently pre-allocated and never need to change.

Overall, FrozenIndex performs very well. Its speed benefit is especially pronounced when fetching large numbers of 
objects, since there is no "object-id-to-object" dict lookup needed. 

Big thanks go to Frank Sauerburger for writing [sortednp](https://pypi.org/project/sortednp/). That library 
makes the union / intersection operations really fly here.
