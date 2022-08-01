# HashBox

Container for finding Python objects by their attributes. Built on hash-based containers (`dict` and `set`), so it's 
very fast.

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
 - FrozenHashBox: much faster performance, memory-efficient, and immutable.

____

## Examples

### Match multiple values

Specify a list of values for an attribute to include / exclude values in the list.

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

### Nested attributes

Define a function to access nested attributes.

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

### Derived attributes

Find-by-function adds huge flexibility. Here we find string objects with certain characteristics.

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
 - [Wordle solver](examples/wordle.ipynb) - Demonstrates using `functools.partials` to make many attribute functions
 - [Collision detection](examples/collision.py) - Find objects based on type and proximity (grid-based)
 - [Percentiles](examples/percentile.py) - Find by percentile (median, p99, etc.)
 - [Crossword helper service](examples/crossword.py) - Pickle a FrozenHashBox, wrap it in an API

____

## Performance

Demo: [HashBox going 5x~10x faster than SQLite](examples/perf_demo.ipynb)

____

## How it works

Attribute values are stored by their hash, either in dicts (HashBox) or numpy 
arrays (FrozenHashBox). So values don't need to be comparable by greater than / less than, they only need to be 
hashable. This maximizes flexibility.

For each attribute value, a [unique ID](https://docs.python.org/3/library/functions.html#id) of each matching object is 
stored. During `find`, these IDs are retrieved as sets (HashBox) or
[sorted numpy arrays](https://pypi.org/project/sortednp/) (FrozenHashBox). Set operations 
such as intersection are then used to find the objects that fit all constraints.

____
