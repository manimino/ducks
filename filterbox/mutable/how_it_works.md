## How It Works, Mutable Edition

Here's more detailed pseudocode of a FilterBox:

```
class FilterBox:
    # holds each attribute index and the id-to-object map
    indexes = {
        'attr1': MutableAttrIndex(),
        'attr2': MutableAttrIndex()
    }
    'obj_map': {obj_ids: objects}
}


class MutableAttrIndex: 
    # maps the values for one attribute to object IDs
    tree = BTree({
        val1: set(some_obj_ids), 
        val2: set(other_obj_ids)
    })
```

On `FilterBox.find()`:
 - FilterBox breaks the query down into individual attribute value lookups.
 - The object IDs associated with the query attribute values are retrieved from MutableAttrIndex.
 - Set operations like `intersect` are performed on the object IDs to get a final set.
 - The object IDs are mapped to objects, which are then returned.

## Memory efficiency

There are a few more implementation details worth noting. But first, let's look at the driving force
behind those details. We need to store lots of collections of integer object IDs - what's the most RAM-efficient way to 
do that?

### Bytes per integer, by collection size

Let's do some measuring of collection overhead. We'll store 10 million distinct int64s in collections of each
type, and vary the size of the collections. 

We expect bigger collections to be more efficient (fewer bytes per object). Ten million sets of size 1 should 
take up more RAM than ten sets of size 1 million.

Results:

|                     | 1     | 2     | 3     | 4    | 5     | 10    | 25    | 50   | 100   | 1000  | 10000 |
|---------------------|-------|-------|-------|------|-------|-------|-------|------|-------|-------|-------|
| set                 | 260.1 | 146.3 | 108.4 | 89.4 | 195.0 | 113.8 | 124.2 | 78.3 | 116.9 | 65.5  | 85.5  |
| tuple               | 89.7  | 69.4  | 57.3  | 55.4 | 50.9  | 47.0  | 43.1  | 41.8 | 41.1  | 40.6  | 40.5  |
| cykhash Int64Set    | 160.1 | 79.9  | 53.1  | 47.7 | 38.1  | 25.3  | 15.5  | 23.5 | 22.4  | 17.1  | 13.7  |
| numpy array (int64) | 161.1 | 80.3  | 53.4  | 43.9 | 35.0  | 22.1  | 13.5  | 10.9 | 9.4   | 8.2   | 8.4   |
| array (int64)       | 106.0 | 53.2  | 35.6  | 26.8 | 28.0  | 21.0  | 11.6  | 10.6 | 9.1   | 8.3   | 8.1   |

That table tells us a story:
 - Small collections of any type are extremely inefficient. Don't make collections of size 1.
 - Immutable collections are cheaper. Tuples, arrays, and numpy arrays cost less memory than the set types.
 - Typed collections are cheaper. Numpy arrays and [cykhash](https://github.com/realead/cykhash) Int64Sets are cheaper than tuples or Python sets.

The best collection in terms of memory usage is a big array. But FilterBox is mutable; we need to add and remove
objects in a few microseconds. Rewriting a big array on change is too slow. So we'll save the arrays for 
`FrozenFilterBox`. 

### Blending collection types

For smaller collections, below ~10 numbers, cykhash is a bit inefficient, so we use arrays there instead.
While they are immutable, it's fast to discard a small array and make another one.

And for collections of size 1... we just store the number, no container needed! That takes 28 bytes.

So the code is a bit more complex than the pseudocode above, in order to keep collection overhead from filling RAM.

Here is the table again. FilterBox (line 3) uses cykhash, array, and integer types to stay RAM-efficient at all 
collection sizes.

|                     | 1     | 2     | 3     | 4    | 5     | 10    | 25    | 50   | 100   | 1000  | 10000 |
|---------------------|-------|-------|-------|------|-------|-------|-------|------|-------|-------|-------|
| set                 | 260.1 | 146.3 | 108.4 | 89.4 | 195.0 | 113.8 | 124.2 | 78.3 | 116.9 | 65.5  | 85.5  |
| cykhash Int64Set    | 160.1 | 79.9  | 53.1  | 47.7 | 38.1  | 25.3  | 15.5  | 23.5 | 22.4  | 17.1  | 13.7  |
| array (int64)       | 106.0 | 53.2  | 35.6  | 26.8 | 28.0  | 21.0  | 11.6  | 10.6 | 9.1   | 8.3   | 8.1   |
| FilterBox storage   | 28.0  | 53.2  | 35.6  | 26.8 | 28.0  | 21.0  | 15.5  | 23.5 | 22.4  | 17.1  | 13.7  |

That's 4 to 10 times better than naively using Python sets to store ints, with no measurable impact on find speed.
