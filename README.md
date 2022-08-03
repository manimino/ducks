# HashBox

Container for finding Python objects by matching attributes. 

Uses hash-based methods for storage and retrieval, so find is very fast.

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

Expand for sample code.

<details>
<summary>Specify a list of values for an attribute to include / exclude values in the list.</summary>
<br>


```
from hashbox import HashBox

objects = [
    {'order': 1, 'size': 'regular', 'topping': 'smothered'}, 
    {'order': 2, 'size': 'regular', 'topping': 'diced'}, 
    {'order': 3, 'size': 'large', 'topping': 'covered'},
    {'order': 4, 'size': 'triple', 'topping': 'chunked'}
]

hb = HashBox(objects, on=['size', 'topping'])

hb.find(
    match={'size': ['regular', 'large']},  # match anything with size in ['regular', 'large'] 
    exclude={'topping': 'diced'}           # exclude where topping is 'diced'
)  # result: orders 1 and 3

hb.find(
    match={},                               # match all objects
    exclude={'size': ['regular', 'large']}  # where size is not in ['regular', 'large']
)  # result: order 4

```
</details>

<details>
<summary>Define a function to access nested attributes.</summary>


```
from hashbox import HashBox

class Order:
    def __init__(self, num, size, toppings):
        self.num = num
        self.size = size
        self.toppings = toppings
        
    def __repr__(self):
        return f"order: {self.num}, size: '{self.size}', toppings: {self.toppings}"
    
objects = [
    Order(1, 'regular', ['scattered', 'smothered', 'covered']),
    Order(2, 'large', ['scattered', 'covered', 'peppered']),
    Order(3, 'large', ['scattered', 'diced', 'chunked']),
    Order(4, 'triple', ['all the way']),
]

def has_cheese(obj):
    return 'covered' in obj.toppings or 'all the way' in obj.toppings

hb = HashBox(objects, ['size', has_cheese])

# returns orders 1, 2 and 4
hb.find({has_cheese: True})  
```
</details>


<details>
<summary>Derived attributes</summary>
<br />
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
</details>

### Recipes
 
 - [Auto-updating](https://github.com/manimino/hashbox/blob/main/examples/update.py) - Keep HashBox updated when attribute values change
 - [Wordle solver](https://github.com/manimino/hashbox/blob/main/examples/wordle.ipynb) - Demonstrates using `functools.partials` to make attribute functions
 - [Collision detection](https://github.com/manimino/hashbox/blob/main/examples/collision.py) - Find objects based on type and proximity (grid-based)
 - [Percentiles](https://github.com/manimino/hashbox/blob/main/examples/percentile.py) - Find by percentile (median, p99, etc.)
 - [Missing attributes in functions](https://github.com/manimino/hashbox/blob/main/examples/missing_function.py) - How to handle missing attributes in attribute functions

____

## Performance

Demo: [HashBox going 5x~10x faster than SQLite](https://github.com/manimino/hashbox/blob/main/examples/perf_demo.ipynb)

____

## How it works

In HashBox, each attribute is a dict of sets: `{attribute value: set(object IDs)}`. 
On `find()`, object IDs are retrieved for each attribute value. Then, set operations are applied to get the final
object ID set. Last, the object IDs are mapped to objects, which are then returned.

FrozenHashBox uses arrays instead of sets, thanks to its immutability constraint. It stores a numpy array 
of objects. Attribute values map to indices in the object array. On `find()`, the array indices for each match are 
retrieved. Then, set operations provided by [sortednp](https://pypi.org/project/sortednp/) are used to get a 
final set of object array indices. Last, the objects are retrieved from the object array by index and returned.

HashBox and FrozenHashBox are sparse: If an object is missing an attribute, the link from that attribute to the object
is not stored. This improves memory efficiency when handling diverse objects.

### Related projects

HashBox is a type of inverted index. It is optimized for its goal of finding in-memory Python objects.

Other Python inverted index implementations are aimed at things like [vector search](https://pypi.org/project/rii/) and
[finding documents by words](https://pypi.org/project/nltk/). Outside of Python, ElasticSearch is a popular inverted
index search tool. Each of these has goals outside of HashBox's niche; there are no plans to expand HashBox towards
these functions.

____

<div align="center">
  <img src="https://github.com/manimino/hashbox/blob/add_logo/img/hashbox-logo.png"><br>
</div>
