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

This is a Dex of dicts, but the objects can be any type, `even primitives like strings. <https://ducks.readthedocs.io/en/latest/quick_start.html#function-attributes>`_

Dex supports ==, !=, in, not in, <, <=, >, >=.

The indexes can be dict keys, object attributes, or custom functions.

--------------
Is ducks fast?
--------------

Yes. Here's how ducks compares to other object-finders on an example task.

.. image:: https://raw.githubusercontent.com/manimino/ducks/main/docs/img/perf_bench.png
    :width: 600

`Notebook for this chart <https://github.com/manimino/ducks/blob/main/examples/perf_demo.ipynb>`_

The Dex and `FrozenDex <https://ducks.readthedocs.io/en/latest/quick_start.html#frozendex>`_ containers in ducks
are well optimized. See the `How It Works <https://ducks.readthedocs.io/en/latest/how_it_works.html>`_ doc for
details.

----
Docs
----

The `Quick Start <https://ducks.readthedocs.io/en/latest/quick_start.html>`_ doc covers a few more things, like
pickling, nested attribute handling, and concurrency.
