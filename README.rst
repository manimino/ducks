=====
ducks
=====

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

Is Dex fast?
============

Yes. Here's how Dex compares to other object-finders on an example task.

.. image:: img/perf_bench.png

`Benchmark source <https://github.com/manimino/ducks/blob/main/examples/perf_demo.ipynb>`_

The closest thing to a Dex is an in-memory SQLite. While SQLite is a fantastic database, it requires
more overhead. As such, Dex is generally faster.
