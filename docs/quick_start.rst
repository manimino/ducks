===========
Quick Start
===========

-----------
Basic Usage
-----------

The main container in ducks is called Dex.

.. code-block::

    from ducks import Dex

    # make some objects
    objects = [
        {'x': 3, 'y': 'a'},
        {'x': 6, 'y': 'b'},
        {'x': 9, 'y': 'c'}
    ]

    # Create a Dex containing the objects.
    # Index on x and y.
    dex = Dex(objects, ['x', 'y'])

    # match objects
    dex[{
        'x': {'>': 5, '<': 10},  # where 5 < x < 10
        'y': {'in': ['a', 'b']}  # and y is 'a' or 'b'
    }]
    # result: [{'x': 6, 'y': 'b'}]

This is a Dex of dicts, but the objects can be any type.

Dex supports ==, !=, in, not in, <, <=, >, >=.

The indexes can be dict keys, object attributes, or custom functions.

-------------------
Add, remove, update
-------------------

Dex supports add, remove, and update of objects.

.. code-block::

    from ducks import Dex

    class Thing:
        def __init__(self):
            self.x = 1
            self.y = 1

        def __repr__(self):
            return f"Thing(x: {self.x}, y: {self.y})"

    # make an empty Dex
    dex = Dex([], ['x', 'y'])

    # add an object
    obj = Thing()
    dex.add(obj)
    print(dex[{'x': 1}]) # find it

    # update it
    obj.x = 2
    dex.update(obj)
    print(dex[{'x': 2}])  # find updated obj

    # remove it
    dex.remove(obj)
    print(list(dex))  # dex now contains no objects

Update notifies Dex that an object's attributes have changed, so the index can be updated accordingly.
There's an example in :ref:`demos` of how to automatically update Dex when objects change.

---------
FrozenDex
---------

If you don't need add, remove, or update, use a FrozenDex instead.
It is used just like a Dex, but it's faster and more memory-efficient.

.. code-block::

    from ducks import FrozenDex

    dex = FrozenDex([{'a': 1, 'b': 2}], ['a'])
    dex[{'a': 1}]  # result: [{'a': 1, 'b': 2}]

-------------------
Function attributes
-------------------

Objects such as strings will not have attributes.
That's OK. Dex can also index using functions evaluated on the object.

Let's find all the strings that are palindromes of length 3:

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

    print(dex[{'a': ANY}])          # [{'a': 1}, {'a': 2}]
    print(dex[{get_a: ANY}])        # [{'a': 1}, {'a': 2}]
    print(dex[{'a': {'!=': ANY}}])  # [{}]

Note that ``None`` is treated as a normal attribute value and is stored.

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

-------
Classes
-------

There are three container classes:

* **Dex**: Can add, remove, and update objects after creation.
  `[API] <https://ducks.readthedocs.io/en/latest/ducks.mutable.html#ducks.mutable.main.Dex>`_
* **ConcurrentDex**: Same as Dex, but thread-safe.
  `[API] <https://ducks.readthedocs.io/en/latest/ducks.concurrent.html#ducks.concurrent.main.ConcurrentDex>`_
* **FrozenDex**: Cannot be changed after creation, it's read-only. But it's super fast. And it's thread-safe because
  it's read-only. `[API] <https://ducks.readthedocs.io/en/latest/ducks.frozen.html#ducks.frozen.main.FrozenDex>`_
