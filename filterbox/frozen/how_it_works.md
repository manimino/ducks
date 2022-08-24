## How It Works, Frozen Edition


### Implementing BTree-of-set using Numpy arrays

In FrozenFilterBox, we know that:
 - The data will never change
 - The values are always integers

This means we can use an array-based implementation rather than a tree. This design is much faster and far more 
memory-efficient. Bisecting a sorted array allows O(log(n)) lookup, just like a tree, while not incurring the various
overheads that a tree does. 

Pseudocode:
```
class FrozenFilterBox:
    # holds each attribute index and an array of objects
    indexes = {
        'attr1': FrozenAttrIndex(),
        'attr2': FrozenAttrIndex()
    }
    'objects': np.array(dtype="O")  
}

class MutableAttrIndex: 
    # maps the values for an attribute to object array indexes
    
    val_arr = np.array(attribute value for each object)  # sorted by value
    obj_idx_arr = np.array(index in obj array for each object)  # sorted by value
    
    # tree stores values for which there are many matching objects
    tree = BTree({
        val1: np.array(sorted_obj_arr_indexes),
        val2: np.array(sorted_obj_arr_indexes)
    })
```

Rather than having a dict lookup for object id -> object, we just store the objects in an array. Instead of
object IDs, we can use indexes into that array. Handily, the indexes can be `int32` if there are less than a few
billion objects, which is usually the case. `int32` operations are a little faster than `int64`, in addition to being 
more RAM-efficient.


### Set operations on numpy arrays

If you have the arrays:

```
[1, 3, 5, 7]
[1, 2, 3, 4, 5, 6, 7]
```

What is their intersection? Do you need to convert them to `set` to figure it out? 

Of course not -- sorted array intersection is easy. There's a great package called 
[sortednp](https://pypi.org/project/sortednp/) that implements fast set operations on sorted numpy arrays.

So once we have the object indexes for each part of a query, `sortednp.intersect` and friends will get us the final
object indexes.

### Wrap up

Using low-level array operations is wonderful when you can do it. The FrozenFilterBox performance and efficiency
are very good.

Further optimization would probably look like:
 - Numba, which was not used due to requirements conflicts (it's pretty restrictive)
 - Rewriting in a compiled language
 - Bypassing the GIL
 - Running in a distributed form (many FrozenFilterBox services executing queries in parallel)

But within the limits of being a versatile Python container - this is probably the best you can get.
