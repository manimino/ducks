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

In this benchmark, two million objects are generated. Each datastore is used to find the subset of 200 of them that match
four constraints. The ducks containers Dex and FrozenDex are shown to be very efficient at this, outperforming by 5x and
and 10x respectively.

Benchmark code is `in the Jupyter notebook <https://github.com/manimino/ducks/blob/main/examples/perf_demo.ipynb>`_.

----
Docs
----

`Quick Start <https://ducks.readthedocs.io/en/latest/quick_start.html>`_ covers all the features you need, like
pickling, nested attribute handling, and thread concurrency.

`How It Works <https://ducks.readthedocs.io/en/latest/how_it_works.html>`_ is a deep dive on the implementation details.

`Demos <https://ducks.readthedocs.io/en/latest/demos.html>`_ has short scripts showing example uses.
