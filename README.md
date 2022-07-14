# HashIndex

[![tests Actions Status](https://github.com/manimino/hashindex/workflows/tests/badge.svg)](https://github.com/manimino/hashindex/actions)

Find Python objects by exact match on their attributes.

`pip install hashindex`

## Usage

```
from hashindex import HashIndex

objects = [
    {'order': 1, 'size': 'regular', 'topping': 'smothered'}, 
    {'order': 2, 'size': 'regular', 'topping': 'diced'}, 
    {'order': 3, 'size': 'large', 'topping': 'covered'},
    {'order': 4, 'size': 'triple', 'topping': 'chunked'}
]

hi = HashIndex(objects, on=['size', 'topping'])

# returns order 1
hi.find(match={'size': 'regular', 'topping': 'smothered'})  

# returns orders 1 and 2
hi.find(
    match={'size': ['regular', 'large']},  # match 'regular' or 'large' sizes
    exclude={'topping': 'covered'}         # exclude where topping is 'covered'
)
```

____

## Features

 - Any Python object can be indexed: class instances, namedtuples, dicts, strings, floats, ints, etc. 
 - The objects do not need to be hashable. They are not serialized, copied, or persisted. HashIndex is just a container.
 - The attributes must be hashable, though.
 - Functions of the objects can also be indexed. This allows for indexing nested data and many more applications.
 - If an object is missing an attribute, it will be indexed with a `None` value for that attribute.
 - HashIndex is mutable; `add`, `remove` and `update` of objects is supported.
 - If you do not need mutability, `FrozenHashIndex` is the immutable version. It is faster, more RAM-efficient, and 
thread-safe.
 - HashIndex and FrozenHashIndex have been optimized for memory efficiency and speed. 
 - They scale well. You can store a billion items in a HashIndex or FrozenHashIndex. It will take up about 20GB of RAM.

____

## How it works

At a high level, you can think of each attribute index as a dict of set of object IDs. An attribute lookup
finds a set of object IDs. Then union / intersection / difference operations are performed on the results of those
lookups to find the object IDs matching the query constraints. The object corresponding to each ID is returned. 

In practice, dict-of-set does not perform well, especially on high-cardinality data. So instead, HashIndex uses data 
structures that deliver the same workflow but with far better memory efficiency and lookup speed.

[See design for details.](docs/design.md)

____

## More Examples

### Nested attributes

```
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
    
hi = HashIndex(objects, ['size', has_cheese])

# returns orders 1, 2 and 4
hi.find({has_cheese: True})  
```

### String objects

```
objects = ['one', 'two', 'three']

def e_count(obj):
    return obj.count('e')

hi = HashIndex(objects, [e_count, len])
hi.find({len: 3})       # returns ['one', 'two']
hi.find({e_count: 2})  # returns ['three']
```

### Bigger examples
 
 - [Document search]()
 - [Wordle solver]()

____

## HashIndex API

### 

____

## FrozenIndex API

____

## Performance


