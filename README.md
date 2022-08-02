# HashBox

Container for finding Python objects by matching attributes. 

Uses hash-based methods for storage and retrieval, so finds are very fast.

```
pip install hashbox
```

[![tests Actions Status](https://github.com/manimino/hashbox/workflows/tests/badge.svg)](https://github.com/manimino/hashbox/actions)
[![Coverage - 100%](https://img.shields.io/static/v1?label=Coverage&message=100%&color=2ea44f)](test/cov.txt)
[![license - MIT](https://img.shields.io/static/v1?label=license&message=MIT&color=2ea44f)](/LICENSE)
![python - 3.7+](https://img.shields.io/static/v1?label=python&message=3.7%2B&color=2ea44f)


### Usage:

```
from hashbox import HashBox

objects = [
    {'a': 1, 'b': 2}, 
    {'a': 1, 'b': 3}
]

hb = HashBox(
    objects,
    on=['a', 'b']
)

hb.find(
    match={'a': 1}, 
    exclude={'b': 3}
)  
# result: [{'a': 1, 'b': 2}]
```

The objects can be any type: class instances, namedtuples, dicts, strings, floats, ints, etc.

There are two classes available.
 - HashBox: can `add()` and `remove()` objects.
 - FrozenHashBox: faster finds, lower memory usage, and immutable.

____

## Examples

### Match multiple values

Specify a list of values for an attribute to include / exclude values in the list.
 - `match={'a': [1, 2, 3]}` matches all objects where 'a' equals 1, 2, or 3. (Read as `obj['a'] in [1, 2, 3]`).
 - `exclude={'b': [4, 5, 6]}` excludes objects where 'b' is 4, 5, or 6. (Read as `obj['b'] not in [4, 5, 6]`).

[Sample code](examples/match_list.py)

### Nested attributes

Define functions to access nested attributes. The functions can be used as attributes.

```
def get_nested_attribute(obj):
    return obj.arr[3]  # gets the third array element of obj.arr
hb = HashBox(objs, [get_nested_attribute])
```

[Sample code](examples/nested_attributes.py)


### Derived attributes

Find-by-function is very powerful. Here we find string objects with certain characteristics.

```
from hashbox import FrozenHashBox

objects = ['mushrooms', 'peppers', 'onions']

def o_count(obj):
    return obj.count('o')

f = FrozenHashBox(objects, [o_count, len])
f.find({len: 6})       # returns ['onions']
f.find({o_count: 2})   # returns ['mushrooms', 'onions']
```

### Recipes
 
 - [Auto-updating](examples/update.py) - Keep HashBox updated when attribute values change
 - [Wordle solver](examples/wordle.ipynb) - Demonstrates using `functools.partials` to make attribute functions
 - [Collision detection](examples/collision.py) - Find objects based on type and proximity (grid-based)
 - [Percentiles](examples/percentile.py) - Find by percentile (median, p99, etc.)
 - [Missing attributes in functions](examples/missing_function.py) - How to handle missing attributes in attribute functions

____

## Performance

Demo: [HashBox going 5x~10x faster than SQLite](examples/perf_demo.ipynb)

____

## How it works

In HashBox, each attribute is a dict of sets: `{attribute value: set(object IDs)}`. 
On `find()`, object IDs are retrieved for each attribute value, and set operations are applied to get the final
object ID set. Last, the object IDs are mapped to objects, which are then returned.

FrozenHashBox uses arrays instead of sets, thanks to its immutability constraint. It stores a numpy array 
of objects. Attribute values map to indices in the object array. On `find()`, the array indices for each match are 
retrieved. Then, very fast set operations provided by [sortednp](https://pypi.org/project/sortednp/) are used to get a 
final set of object array indices. The objects are retrieved from the object array by index and returned.

HashBox and FrozenHashBox are sparse: If an object is missing an attribute, the link from that attribute to the object
is not stored. This improves memory efficiency when handling diverse objects.

### Related projects

HashBox is a type of inverted index. It is optimized for its goal of finding in-memory Python objects.

Other Python inverted index implementations are aimed at things like [vector search](https://pypi.org/project/rii/) and
[finding documents by words](https://pypi.org/project/nltk/). Outside of Python, ElasticSearch is a popular inverted
index search tool. Each of these has goals outside of HashBox's niche; there are no plans to expand HashBox towards
these functions.

____
