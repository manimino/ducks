=========
ducks  🦆
=========

Index your Python objects for fast lookup by their attributes.

.. image:: https://github.com/manimino/ducks/workflows/tests/badge.svg
    :target: https://github.com/manimino/ducks/actions
    :alt: tests Actions Status
.. image:: https://img.shields.io/static/v1?label=Coverage&message=100%&color=2ea44f
    :target: https://github.com/manimino/ducks/blob/main/test/cov.txt
    :alt: Coverage - 100%
.. image:: https://img.shields.io/static/v1?label=license&message=MIT&color=2ea44f
    :target: https://github.com/manimino/ducks/blob/main/LICENSE
    :alt: license - MIT
.. image:: https://img.shields.io/static/v1?label=python&message=3.7%2B&color=2ea44f
    :target: https://github.com/manimino/ducks/
    :alt: python - 3.7+

Install
=======

.. code-block::

    pip install ducks

Usage
=====

The main container in ducks is called Dex.

.. code-block::

    from ducks import Dex

    objects = [
        {'x': 3, 'y': 'a'},
        {'x': 6, 'y': 'b'},
        {'x': 9, 'y': 'c'}
    ]

    # Create a Dex containing the objects.
    # Index on x and y.
    dex = Dex(objects, ['x', 'y'])

    # get objects
    dex[{
        'x': {'>': 4, '<': 8},   # where 4 < x < 8
        'y': {'in': ['a', 'b']}  # and y is 'a' or 'b'
    }]
    # result: [{'x': 6, 'y': 'b'}]

* This is a Dex of dicts, but the objects can be any type.
* Dex supports ==, !=, in, not in, <, <=, >, >=.
* The indexes can be dict keys, object attributes, and custom functions.

Is Dex fast?
============

Yes. Here's how Dex compares to other object-finders on an example task.

.. image:: https://github.com/manimino/ducks/blob/main/docs/img/perf_bench.png

`Benchmark source <https://github.com/manimino/ducks/blob/main/examples/perf_demo.ipynb>`_

The closest thing to a Dex is an in-memory SQLite. While SQLite is a fantastic database, it requires
more overhead. As such, Dex is generally faster.

Is Dex a database?
==================

No. But like a database, Dex uses B-tree indexes and uses them to find results very quickly. It does
not any do other database things like SQL, tables, etc. This keeps Dex simple, light, and performant.

Docs
====

There's more to ducks than making a Dex of dicts.

`See the docs. <https://ducks.readthedocs.io/en/latest/quick_start.html>`_