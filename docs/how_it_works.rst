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
memory usage and speed than a naive implementation. For example, FrozenDex uses an array-based tree structure.

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
            val1: set(some_obj_ids),
            val2: set(other_obj_ids)
        })
    ```

To run a query:

#. Dex breaks the query down into individual attribute value lookups.
#. The object IDs associated with the query attribute values are retrieved from MutableAttrIndex.
#. Set operations like `intersect` are performed on the object IDs to get a final set.
#. The object IDs are mapped to objects, which are then returned.

Memory efficiency
=================

There are a few more implementation details worth noting. But first, let's look at the driving force
behind those details. We need to store lots of collections of integer object IDs - what's the most RAM-efficient way to
do that?

Memory usage of different collections
=====================================

Let's do some measuring of collection overhead. We'll store 10 million distinct int64s in collections of each
type, and vary the size of the collections.

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

For smaller collections, below ~10 numbers, cykhash is a bit inefficient, so we use arrays there instead.
While they are immutable, it's fast to discard a small array and make another one.

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

In FrozenDex, we know that:

* The data will never change
* The values are always integers

This means we can use an array-based implementation rather than a tree. This design is much faster and far more
memory-efficient. Bisecting a sorted array allows O(log(n)) lookup, just like a tree.

Pseudocode:

.. code-block::

    class FrozenDex:
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


Rather than having a dict lookup for object id -> object, we just store the objects in an array. Instead of
object IDs, we can use indexes into that array. Handily, the indexes can be `int32` if there are less than a few
billion objects, which is usually the case. `int32` operations are a little faster than `int64`, in addition to being
more RAM-efficient.


Set operations on numpy arrays
==============================

If you have the arrays:

.. code-block::

    [1, 3, 5, 7]
    [1, 2, 3, 4, 5, 6, 7]

What is their intersection? Do you need to convert them to ``set`` to figure it out?

Of course not -- sorted array intersection is easy. There's a great package called
`sortednp <https://pypi.org/project/sortednp/>`_ that implements fast set operations on sorted numpy arrays.

So once we have the object indexes for each part of a query, ``sortednp.intersect`` and friends will get us the final
object indexes.

Using low-level array operations is wonderful when you can do it. The FrozenDex performance and efficiency
are very good.

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

Reasons to trust it
===================

Concurrency bugs are notoriously tricky to find. ConcurrentDex is unlikely to have them because:

* It uses a very simple, coarse-grained concurrency that locks the whole object for every read and write
* It's built on a widely-used lock library
* There are concurrent operation tests that succeed on ConcurrentDex and fail on Dex, proving the
  locks are working properly (see ``tests/concurrent``).
