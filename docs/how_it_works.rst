========
Overview
========

For each attribute in a Dex, it holds a B-tree that maps every unique value to the set of objects with
that value.

This is a rough idea of the data structure:

.. code-block::console
    class Dex:
        indexes = {
            'attribute1': BTree({10: set(some_obj_ids), 20: set(other_obj_ids)}),
            'attribute2': BTree({'abc': set(some_obj_ids), 'def': set(other_obj_ids)}),
        }
        obj_map = {obj_ids: objects}
    }

During a lookup, the object ID sets matching each query value are retrieved. Then set operations like `union`,
`intersect`, and `difference` are applied to get the matching object IDs. Finally, the object IDs are converted
to objects and returned.

In practice, Dex and FrozenDex have a bit more to them, as they are optimized to have much better
memory usage and speed than a naive implementation. For example, FrozenDex uses an array-based tree structure.

=============
How Dex works
=============


===================
How FrozenDex works
===================


=======================
How ConcurrentDex works
=======================
