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


Suppose you've got a lot of Python objects in memory. Like a thousand, a million, or even a billion. And you want to
find the ones that match some filter or combination of filters. And you want it to be fast, like a database index is
fast.

Maybe the objects are strings, and you want to find all the strings of length 5 where the first letter is "d" and second letter is "u".

Or they're tuples of points, and you want to find the points inside some bounding box.

Or they're dictionaries, and you want to find ones where a certain key has a certain value, or range of values, or
if the key is missing.

Or they're class instances, and you want to filter them by their attributes.

Or they're rows in a dataframe, and you want to find which rows match your constraints.

If any of those sound like your problem, you're a lucky duck today! Any time you find code that's repeatedly looping
over objects to find matches (e.g. list comprehensions), that code could probably be better using a ducks index.

-------
Install
-------

.. code-block::

    pip install ducks

------------------------
Example 1 - Dictionaries
------------------------

For this example, we'll use dictionaries containing the weather forecast.

.. code-block::
    days = [
        {'day': 'Saturday', 'sky': 'sunny', 'wind_speed': 1},
        {'day': 'Sunday', 'sky': 'rainy', 'wind_speed': 3},
        {'day': 'Monday', 'sky': 'sunny', 'wind_speed': 5},
        {'day': 'Tuesday', 'sky': 'sunny', 'wind_speed': 7},
        {'day': 'Wednesday', 'sky': 'sunny', 'wind_speed': 25}
    ]

Now we build an index on the attributes of interest.

.. code-block::
    from ducks import Dex

    dex = Dex(                    # make a Dex
        days,                     # add objects of any Python type
        on=['sky', 'wind_speed']  # specify what to index on
    )

And last, we query the index.

.. code-block::
    # Find all the sunny days
    dex[{'sky': sunny}]

    # Find the very windy day
    dex[{'wind_speed': {'>': 20}}]

    # Find comfy days, that are sunny and a bit windy, but not _too_ windy.
    dex[{'sky': 'sunny', 'wind_speed': {'>=': 5, '<': 10}}]

Note that you can use any combination of the attributes in the index. So here you can query by 'sky', 'wind_speed', or
both.

-------------------------------
Example 2 - Function attributes
-------------------------------

Now we're going to show off something more powerful. We're going to index objects based on the results of functions
applied to them.

Here we'll use it to find strings that are palindromes.

.. code-block::
    from ducks import Dex

    # Let's make some strings
    strings = ['bob', 'fives', 'kayak', 'stats', 'pullup', 'racecar']

    # define a function that takes in one object and returns a single value
    def is_palindrome(s):
        return s == s[::-1]

    # build an index on is_palindrome and the len function
    dex = Dex(strings, [is_palindrome, len])

    # find palindromes of length 5 or 7
    dex[{is_palindrome: True, len: {'in': [5, 7]}}]
    # result: ['kayak', 'racecar', 'stats']

Indexing on functions allows you to work with primitives like strings, which don't have useful attributes.
Effectively, you can use functions to define your own attributes to index on.

------------
And the rest
------------

Dex is a normal Python container, so you can loop over its contents with ``for object in dex``. You can add an object
with ``dex.add(object)``, remove with ``dex.remove(object)``, and update with ``dex.update(object)``.

If you want a read-only Dex that queries even faster and uses less memory, use FrozenDex. It's just like Dex,
but you can't add / remove / update.

And if you need to share a Dex in a multithreaded environment, there's ConcurrentDex. Again, works just like Dex.

That's everything you need to know!

-----------
Performance
-----------

Here's how the ducks containers compare to other datastores on an example filtering task.

.. image:: https://raw.githubusercontent.com/manimino/ducks/main/docs/img/perf_bench.png
    :width: 600

In this benchmark, two million objects are generated. Each datastore is used to find the subset of 200 of them that match
four constraints. The ducks containers Dex and FrozenDex are shown to be very efficient at this, outperforming by 5x and
and 10x respectively.

Benchmark code is `in the Jupyter notebook <https://github.com/manimino/ducks/blob/main/examples/perf_demo.ipynb>`_.

----
Docs
----

`Examples <https://ducks.readthedocs.io/en/latest/examples.html>`_ has code to demonstrate other things you might need,
like pickling, nested attribute handling, and thread concurrency.

`How It Works <https://ducks.readthedocs.io/en/latest/how_it_works.html>`_ is a deep dive on the implementation details.

`Demos <https://ducks.readthedocs.io/en/latest/demos.html>`_ shows some more complex, real-world like examples.
