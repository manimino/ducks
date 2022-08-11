## How It Works, Frozen Edition

**Note: This assumes familiarity with the regular FilterBox.**

### Implementing dict-of-set using Numpy arrays

In FrozenFilterBox, we know that:
 - The data will never change
 - The values are always integers

So rather than using a Python `dict of set of object IDs` like FilterBox does, FrozenFilterBox uses numpy arrays to 
achieve the same thing. This design is much faster and far more memory-efficient.

Let's look at the structure of a "dict of set as arrays" implementation.

Suppose we have keys A, B, C, and D. 
 - A hashes to 1
 - B hashes to 2
 - C and D both hash to 3

So we have the arrays:
```
keys    = [A, B, B, D, D, C, C, C]  # keys sorted by hash and grouped by key
hashes  = [1, 2, 2, 3, 3, 3, 3, 3]  # sorted by hash
obj_ids = [z, h, x, y, n, m, q, r]  # object IDs that we will look up by key

# compute these by run-length-encoding of the hashes array
unique_hashes   = [1, 2, 3]
hash_start_pos  = [0, 1, 3]
hash_run_length = [1, 2, 5]
```

Now let's find the object IDs that match the key B.
 - Hash B to 2
 - Find that 2 is in unique_hashes (it's a sorted array, so this takes log(n))
 - Find start and end positions using hash_start_pos and hash_run_length.
 - hash_start_pos = 1 and hash_run_length = 2, so we'll check keys at positions 1 and 2.
 - The keys at positions 1 and 2 are both B. Get their obj_ids.
 - Return object IDs `[h, x]`.

What if we wanted the object ID for key C? It has the same hash as D does -- how will that work?
 - Hash C to 2
 - Find that C is in unique_hashes (it's a sorted array, so this takes log(n))
 - Find start and end positions using hash_start_pos and hash_run_length.
 - hash_start_pos = 3 and hash_run_length = 5, so we'll check keys in the range (3, 3+5).
 - Initialize a pointer at 3 and a pointer at 8. Move them towards each other, stopping on the first C.
 - Keys 5, 6, and 7 are all C.
 - Return object IDs `[m, q, r]`.

Note that we never sort by value here. There's a good reason for it; the values may not be comparable.
Maybe A is a string, B is an int, and C is a tuple. Each is hashable, but defining a `<` on them wouldn't make sense.
That's part of the fun of making a container in Python - you never know what types you're going to get!

Note also that we didn't use the `hashes` array during lookup. It is not actually stored, it's just shown in
this example for clarity.

### Set operations on numpy arrays

If you have the arrays:

```
[1, 3, 5, 7]
[1, 2, 3, 4, 5, 6, 7]
```

What is their intersection? Do you need to convert them to `set` to figure it out? 

Of course not -- sorted array intersection is easy. There's a great package called 
[sortednp](https://pypi.org/project/sortednp/) that implements fast operations on sorted numpy arrays.

So once we have the object IDs for each part of a query, `sortednp.intersect` and friends will get us the final
ID set.

Since we're using parallel numpy arrays, the object IDs are not from Python `id()` here; they are actually just
indices into a numpy array of objects stored in FrozenFilterBox. 

### Wrap up

Using low-level array operations is wonderful when you can do it. The FrozenFilterBox performance and efficiency
are very good.

Further optimization would probably look like:
 - Numba, which was not used due to requirements conflicts (it's pretty restrictive)
 - Rewriting in a compiled language
 - Bypassing the GIL
 - Running in a distributed form (many FrozenFilterBox services executing queries in parallel)

But within the limits of being a versatile Python container - this is probably the best you can get.
