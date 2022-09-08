===============
How ducks works
===============

For each attribute in a Dex, it holds a B-tree that maps every unique value to the objects with that value.

This is a rough idea of the data structure:

.. code-block::

    class Dex:
        indexes = {
            'attribute1': BTree({10: set(some_obj_ids), 20: set(other_obj_ids)}),
            'attribute2': BTree({'abc': set(some_obj_ids), 'def': set(other_obj_ids)}),
        }
        obj_map = {obj_ids: objects}
    }

During a lookup, the object ID sets matching each query value are retrieved. The set operations `union`,
`intersect`, and `difference` are applied to get the matching object IDs. Finally, the object IDs are converted
to objects and returned.

In practice, Dex and FrozenDex have a bit more to them, as they are optimized to have much better
memory usage and speed than a naive implementation. For example, FrozenDex makes heavy use of sorted Numpy arrays.

-------------
Dex internals
-------------

Here's more detailed pseudocode of a Dex:

.. code-block::

    class Dex:
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
            val1: set_like(some_obj_ids),
            val2: set_like(other_obj_ids)
        })
    ```

To run a query:

#. Dex breaks the query down into individual attribute value lookups.
#. The object IDs associated with the query attribute values are retrieved from MutableAttrIndex.
#. The set-like containers are converted to sets if needed.
#. Operations like `intersect` are performed on the sets to get the final object IDs.
#. The object IDs are mapped to objects, which are then returned.

Memory efficiency
=================

That "set-like container" is there for memory efficiency reasons. Imagine building an index on a million distinct
values. If actual sets were used, we'd get a million sets of size 1. Collections have a lot of overhead, so that would
be a poor choice. We can do better.

Memory usage of different collections
=====================================

First, let's do some measuring of collection overhead. We'll store a large number of distinct int64s in collections of
each type, vary the size of the collections, and check the memory usage per object.

We expect bigger collections to be more efficient (fewer bytes per object). Ten million sets of size 1 should
take up more RAM than ten sets of size 1 million.

Bytes per entry for each collection type and size:


+-----------------------+---------+---------+---------+---------+---------+--------+---------+
|                       | 1       | 2       | 5       | 10      | 25      | 50     | 100     |
+=======================+=========+=========+=========+=========+=========+========+=========+
| set                   | 260.1   | 146.3   | 195.0   | 113.8   | 124.2   | 78.3   | 116.9   |
+-----------------------+---------+---------+---------+---------+---------+--------+---------+
| tuple                 | 89.7    | 69.4    | 50.9    | 47.0    | 43.1    | 41.8   | 41.1    |
+-----------------------+---------+---------+---------+---------+---------+--------+---------+
| cykhash Int64Set      | 160.1   | 79.9    | 38.1    | 25.3    | 15.5    | 23.5   | 22.4    |
+-----------------------+---------+---------+---------+---------+---------+--------+---------+
| numpy array (int64)   | 161.1   | 80.3    | 35.0    | 22.1    | 13.5    | 10.9   | 9.4     |
+-----------------------+---------+---------+---------+---------+---------+--------+---------+
| array (int64)         | 106.0   | 53.2    | 28.0    | 21.0    | 11.6    | 10.6   | 9.1     |
+-----------------------+---------+---------+---------+---------+---------+--------+---------+

That table tells us a story.

* Small collections of any type are extremely inefficient. Don't make collections of size 1.
* Immutable collections are cheaper. Tuples, arrays, and numpy arrays cost less memory than the set types.
* Typed collections are cheaper. Numpy arrays and `cykhash <https://github.com/realead/cykhash>`_ Int64Sets are cheaper
  than tuples or Python sets.

The best collection in terms of memory usage is a big array. But Dex is mutable; we need to add and remove
objects in a few microseconds. Rewriting a big array on change is too slow. So we'll save the arrays for
FrozenDex. So the single best one for Dex is cykhash Int64Set. By why pick just one?

Blending collection types
=========================

For smaller collections, below ~10 numbers, cykhash is a bit inefficient, so we use Python
int64 arrays there instead. The arrays are immutable, but it's fast to discard a small array and make another one when
changes occur.

And for collections of size 1, we just store the number, no container needed! That takes 28 bytes.

So the code is a bit more complex than the pseudocode above, in order to keep collection overhead from filling RAM.

Here is the table again. Dex (bottom line) uses cykhash, array, and integer types to stay RAM-efficient at all
collection sizes.

+--------------------+---------+---------+---------+--------+---------+--------+---------+
|                    | 1       | 2       | 5       | 10     | 25      | 50     | 100     |
+====================+=========+=========+=========+========+=========+========+=========+
| set                | 260.1   | 146.3   | 195.0   | 113.8  | 124.2   | 78.3   | 116.9   |
+--------------------+---------+---------+---------+--------+---------+--------+---------+
| cykhash Int64Set   | 160.1   | 79.9    | 38.1    | 25.3   | 15.5    | 23.5   | 22.4    |
+--------------------+---------+---------+---------+--------+---------+--------+---------+
| array (int64)      | 106.0   | 53.2    | 28.0    | 21.0   | 11.6    | 10.6   | 9.1     |
+--------------------+---------+---------+---------+--------+---------+--------+---------+
| FilterBox storage  | 28.0    | 53.2    | 28.0    | 21.0   | 15.5    | 23.5   | 22.4    |
+--------------------+---------+---------+---------+--------+---------+--------+---------+

That's 4 to 10 times better than naively using Python sets to store ints. There's no tradeoff;
Int64Set operations are about as fast as Python sets.

-------------------
FrozenDex Internals
-------------------

The FrozenDex implementation is very different from Dex. It is able to achieve better speed and lower memory usage
by using data structures that don't support changes.

FrozenDex pseudocode:

.. code-block::

    class FrozenDex:
        # holds each attribute index and an array of objects
        indexes = {
            'attr1': FrozenAttrIndex(),
            'attr2': FrozenAttrIndex()
        }
        'objects': np.array(dtype="O")
    }

    class FrozenAttrIndex:
        # maps the values for a single attribute to indexes in the 'objects' array

        # parallel arrays store attribute values and object indices
        val_arr = np.array(attribute value for each object)             # sorted by val_arr
        obj_idx_arr = np.array(index in objects array for each object)  # sorted by val_arr

        # but if a value has lots of objects, store it in this tree instead
        tree = BTree({
            value: np.array(sorted_obj_arr_indexes)
        })

Key points:

* The objects are stored in a Numpy array in FrozenDex
* Each FrozenAttrIndex maps values to object array indexes
* FrozenAttrIndex has two different ways to do that mapping - parallel arrays and BTree

Note that there are no "set" types anywhere here - so how do set operations like intersect work?

Sorted arrays are sets
======================

If you have the arrays:

.. code-block::

    [1, 3, 5, 7, 9]
    [1, 2, 3, 4, 5, 6, 7]

What is their intersection? Do you need to convert them to sets to figure it out?

Of course not -- sorted array intersection is easy. It can be solved by iterating over both lists, advancing
the pointer of the smaller value each time, and outputting the matches.
`Galloping search <https://en.wikipedia.org/wiki/Exponential_search>`_ can make this even faster. It is faster than
computing the intersection of hashsets.

FrozenDex uses a great package called
`sortednp <https://pypi.org/project/sortednp/>`_ that implements fast set operations on sorted numpy arrays.
So once we have the object indexes for each part of a query, ``sortednp.intersect`` and friends will get us the final
object indexes.

Sorted arrays are trees
=======================

FrozenDex uses sorted arrays in another way - to store values. Bisecting an array to find a value is similar to
traversing a tree. Range queries are easy on sorted value arrays as well.

So, a FrozenAttrIndex has a pair of arrays, one containing values in sorted order, and the other containing
the object indexes for those values. Looking up the object indexes for a value or range of values is straightforward.

That's not the only way FrozenDex maps values to objects, though. Just as Dex uses different containers depending on
length, so too does FrozenDex.

When a value has many associated objects, storing the value repeatedly in an array is clearly inefficient.
So values that have many objects are stored in a BTree lookup instead. The BTree maps values to arrays of object
indexes.

We can't use the BTree for everything -- if a value is associated with only a few objects, allocating a numpy array to
store the object indexes would incur lots of overhead. So having both data structures is the right way to go.

Integer types
=============

And there's one last optimization. The indexes are stored in `uint32` arrays if there are less than a few
billion objects, which is usually the case. `uint32` operations are a little faster than `uint64`, in addition to being
more RAM-efficient. FrozenDex will automatically select `uint64` when there are too many objects for 32-bit addressing.

Thanks to these optimizations, FrozenDex is a very efficient tool.

-----------------------
ConcurrentDex Internals
-----------------------

ConcurrentDex contains:

* an instance of Dex
* a `readerwriterlock <https://github.com/elarivie/pyReaderWriterLock>`_

It exposes each method of the Dex, wrapped in the appropriate lock type using `with read_lock()` or
`with write_lock()`.

Performance
===========

Each lock operation adds about 5µs. Not huge, but it does add up when doing many operations in a row.

For this reason, the ``read_lock()`` and ``write_lock()`` methods are exposed.

This allows patterns like:

.. code-block::

    cdex = ConcurrentDex(...)
    with cdex.write_lock()
        for item in a_million_items:
            cdex.box.add(item)  # cdex.box is the underlying Dex.

which are faster than calling ``cdex.add()`` many times.

By default, ConcurrentDex favors readers, allowing multiple readers to share a lock. Writers wait for all
readers to release the lock. This behavior is customizable on init via the ``priority`` kwarg.

Reasons to trust it
===================

Concurrency bugs are notoriously tricky to find. ConcurrentDex is unlikely to have them because:

* It uses a very simple, coarse-grained concurrency that locks the whole object at once
* It's built on a widely-used lock library
* There are concurrent operation tests that succeed on ConcurrentDex and fail on Dex, proving the
  locks are working properly (see ``tests/concurrent``).
