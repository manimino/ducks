# HashBox

Container for finding Python objects by exact match on attribute value. 

`pip install hashbox`

[![tests Actions Status](https://github.com/manimino/hashbox/workflows/tests/badge.svg)](https://github.com/manimino/hashbox/actions)
[![Coverage - 100%](https://img.shields.io/static/v1?label=Coverage&message=100%&color=2ea44f)](test/cov.txt)

### Usage:

```
from hashbox import HashBox
f = HashBox(objects, attributes)
objs = f.find(match={attr1: values, ...}, exclude={attr2: values, ...})
```

HashBox can hold any Python object: class instances, namedtuples, dicts, strings, floats, ints, etc.

Attributes can be actual object attributes, or they can be functions of the object. Functions
allow lookup of nested and derived attributes. See examples below.

There are two classes available.
 - HashBox: can `add()` and `remove()` objects.
 - FrozenHashBox: much faster performance and lower memory cost, but can't be changed after creation.

____

## Examples

### Dicts

```
from hashbox import HashBox

objects = [
    {'order': 1, 'size': 'regular', 'topping': 'smothered'}, 
    {'order': 2, 'size': 'regular', 'topping': 'diced'}, 
    {'order': 3, 'size': 'large', 'topping': 'covered'},
    {'order': 4, 'size': 'triple', 'topping': 'chunked'}
]

f = HashBox(objects, on=['size', 'topping'])

f.find(match={'size': 'regular', 'topping': 'smothered'})  # returns order 1

f.find(
    match={'size': ['regular', 'large']},  # match 'regular' or 'large' sizes
    exclude={'topping': 'covered'}         # exclude where topping is 'covered'
)  # returns orders 1 and 2
```

### Object with nested attributes

```
from hashbox import FrozenHashBox

class Order:
    def __init__(self, num, size, toppings):
        self.num = num
        self.size = size
        self.toppings = toppings
    
objects = [
    Order(1, 'regular', ['scattered', 'smothered', 'covered']),
    Order(2, 'large', ['scattered', 'covered', 'peppered']),
    Order(3, 'large', ['scattered', 'diced', 'chunked']),
    Order(4, 'triple', ['all the way']),
]

def has_cheese(obj):
    return 'covered' in obj.toppings or 'all the way' in obj.toppings

f = FrozenHashBox(objects, ['size', has_cheese])

# returns orders 1, 2 and 4
f.find({has_cheese: True})  
```

### Strings

```
from hashbox import FrozenHashBox

objects = ['mushrooms', 'peppers', 'onions']

def o_count(obj):
    return obj.count('o')

f = FrozenHashBox(objects, [o_count, len])
f.find({len: 6})       # returns ['onions']
f.find({o_count: 2})  # returns ['mushrooms', 'onions']
```

### Advanced usage
 
 - [Auto-updating](examples/update.py) - Define setters on your objects to keep HashBox updated when they change
 - [Wordle solver](examples/wordle.ipynb) - Use partials to generate many attribute functions
 - [Spatial lookup](examples/spatial.py) - Do location finding and collision detection

____

## Performance


### FrozenHashBox



### HashBox


____

## How it works

Attribute values are stored by their hash, either in dicts (HashBox) or numpy 
arrays (FrozenHashBox). So values don't need to be comparable by greater than / less than, they only need to be 
hashable. This maximizes flexibility.

For each attribute value, the `id` of each matching object is stored. During `find`, these IDs are retrieved as sets 
(HashBox) or sorted numpy arrays (FrozenHashBox). Set operations such as intersection are then used to find the 
objects that fit all constraints.

____
