===========
Quick Start
===========

-----------
Basic Usage
-----------

.. code-block::

    from ducks import Dex

    objects = [
        {'x': 4, 'y': 1},
        {'x': 6, 'y': 3},
        {'x': 8, 'y': 5}
    ]

    # Create a Dex containing the objects.
    # Index on x and y.
    dex = Dex(objects, ['x', 'y'])

    # get objects
    dex[{
        'x': {'>': 5, '<': 10},  # where 5 < x < 10
        'y': {'in': [1, 2, 3]}   # and y is 1, 2, or 3
    }]
    # result: [{'x': 6, 'y': 3}]

Valid operators are ==, !=, <, <=, >, >=, in, not in.

-------------------
Function attributes
-------------------

You can index on functions evaluated on the object.

Find palindromes of length 3:

.. code-block::

    from ducks import Dex
    strings = [
        'ooh', 'wow',
        'kayak', 'bob'
    ]

    # define a function that
    # takes the object as input
    def is_palindrome(s):
        return s == s[::-1]

    # make a Dex
    dex = Dex(strings, [is_palindrome, len])
    dex[{
        is_palindrome: True,
        len: 3
    }]
    # result: ['wow', 'bob']

Functions are evaluated on the object when it is added to the Dex.

-----------
Nested data
-----------

Use functions to get values from nested data structures.

.. code-block::

    from ducks import Dex

    objs = [
        {'a': {'b': [1, 2, 3]}},
        {'a': {'b': [4, 5, 6]}}
    ]

    def get_nested(obj):
        return obj['a']['b'][0]

    dex = Dex(objs, [get_nested])
    dex[{get_nested: 4}]
    # result: {'a': {'b': [4, 5, 6]}}

------------------
Missing attributes
------------------

Objects don't need to have every attribute.

Indexes are sparse. Objects that are missing an attribute will not be stored
under that attribute. This saves lots of memory.

* To find all objects that have an attribute, match the special value ``ANY``.
* To find objects missing the attribute, do ``{'!=': ANY}``.
* In functions, raise ``MissingAttribute`` to tell ducks the attribute is missing.

Example:

.. code-block::

    from ducks import Dex, ANY, MissingAttribute

    objs = [{'a': 1}, {'a': 2}, {}]

    def get_a(obj):
        try:
            return obj['a']
        except KeyError:
            raise MissingAttribute  # tell Dex this attribute is missing

    dex = Dex(objs, ['a', get_a])

    dex[{'a': ANY}]          # result: [{'a': 1}, {'a': 2}]
    dex[{get_a: ANY}]        # result: [{'a': 1}, {'a': 2}]
    dex[{'a': {'!=': ANY}}]  # result: [{}]

Note that ``None`` is treated as a normal attribute value and is stored.


-------
Classes
-------

There are three container classes:

* **Dex**: Can ``add``, ``remove``, and ``update`` objects after creation.
  `[API] <https://ducks.readthedocs.io/en/latest/ducks.mutable.html#ducks.mutable.main.Dex>`_
* **ConcurrentDex**: Same as Dex, but thread-safe.
  `[API] <https://ducks.readthedocs.io/en/latest/ducks.concurrent.html#ducks.concurrent.main.ConcurrentDex>`_
* **FrozenDex**: Cannot be changed after creation, it's read-only. But it's super fast, and of course thread-safe.
  `[API] <https://ducks.readthedocs.io/en/latest/ducks.frozen.html#ducks.frozen.main.FrozenDex>`_


--------
Pickling
--------

Dex, ConcurrentDex, and FrozenDex can be pickled using the special functions
``save`` and ``load``.

.. code-block::

    from ducks import Dex, save, load
    dex = Dex([1.2, 1.8, 2.7], [round])
    save(dex, 'dex.pkl')
    loaded_dex = load('dex.pkl')
    loaded_dex[{round: 2}]
    # result: 1.8

Objects inside the dex will be saved along with it.
