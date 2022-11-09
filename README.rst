.. image:: https://raw.githubusercontent.com/manimino/ducks/main/docs/img/ducks-main.png
    :alt: Ducks, the Python object indexer

=========
ducks  🦆
=========

Index your Python objects for fast lookup by their attributes.

.. image:: https://img.shields.io/github/stars/manimino/ducks.svg?style=social&label=Star&maxAge=2592000
    :target: https://github.com/manimino/ducks
    :alt: GitHub stars
.. image:: https://github.com/manimino/ducks/workflows/tests/badge.svg
    :target: https://github.com/manimino/ducks/actions
    :alt: tests Actions Status
.. image:: https://codecov.io/github/manimino/ducks/coverage.svg?branch=main
    :target: https://codecov.io/gh/manimino/ducks
    :alt: Coverage
.. image:: https://img.shields.io/static/v1?label=license&message=MIT&color=2ea44f
    :target: https://github.com/manimino/ducks/blob/main/LICENSE
    :alt: license - MIT
.. image:: https://img.shields.io/static/v1?label=python&message=3.7%2B&color=2ea44f
    :target: https://github.com/manimino/ducks/
    :alt: python - 3.7+

-------
Install
-------

.. code-block::

    pip install ducks

-----
Usage
-----

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

This is a Dex of dicts, but the objects can be any type, even primitives like strings.

Dex supports ==, !=, in, not in, <, <=, >, >=.

The indexes can be dict keys, object attributes, or custom functions.

See `Quick Start <https://ducks.readthedocs.io/en/latest/quick_start.html>`_ for more examples of all of these.

--------------
Is ducks fast?
--------------

Yes. Here's how the ducks containers compare to other datastores on an example task.

.. image:: https://raw.githubusercontent.com/manimino/ducks/main/docs/img/perf_bench.png
    :width: 600

In this task, two million objects are generated. Each datastore is used to find the subset of 200 of them that match
four constraints. The ducks containers Dex and FrozenDex are shown to be very efficient at this, winning by 5x and
and 10x respectively.

Full code and discussion `in the Jupyter notebook <https://github.com/manimino/ducks/blob/main/examples/perf_demo.ipynb>`_.

-------------------
Ducks and databases
-------------------

The ducks Dex container is not a database, but it has some database-like characteristics. Much like how a pandas
DataFrame is "database-ish". As pandas has proven, a fancy Python container can be a great fit for many applications that
look database-shaped.

Ducks takes inspiration from a few databases. Spiritually, Ducks is closest to the ElasticSearch / Solr / Lucene.
However, since ducks is not as tailored towards the task of finding documents by words, it uses B-trees
rather than hashmaps - in that way, it's more like most SQL databases. Finally, like Redis, all the objects reside in
memory, rather than living on disk, giving excellent speed.

While it would be possible to store Python objects in any of those datastores, doing so would require serialization. The
objects would have to be copied into strings or binary representations, and stored that way. Since ducks is
operating natively on your Python objects, it does not have this constraint. This means ducks can be much more
efficient. This is especially true when working with objects that have large fields in them such as image data or
feature vectors.

Finally, by being a Python container, ducks can take advantage of the entire Python language. For example, where
databases need special language for things like aggregations or functions, ducks users can just write regular Python.
It is wonderfully convenient to have logic and data live in the same place.

There are many situations to use a database over ducks. If your data is shared by multiple processes, or you
want to write data to disk every time it is changed, or your data can't fit in memory, a database will work better.
But if all you need is to index objects by their attributes, ducks is great.

----
Docs
----

`Quick Start <https://ducks.readthedocs.io/en/latest/quick_start.html>`_ covers all the features you need, like
pickling, nested attribute handling, and thread concurrency.

`How It Works <https://ducks.readthedocs.io/en/latest/how_it_works.html>`_ is a deep dive on the implementation details.

`Demos <https://ducks.readthedocs.io/en/latest/demos.html>`_ has short scripts showing example uses.
