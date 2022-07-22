# HashIndex

Container for finding Python objects by combinations of attributes.

`pip install hashindex`

[![tests Actions Status](https://github.com/manimino/hashindex/workflows/tests/badge.svg)](https://github.com/manimino/hashindex/actions)
[![Coverage - 100%](https://img.shields.io/static/v1?label=Coverage&message=100%&color=2ea44f)](test/cov.txt)

### Usage:

```
from hashindex import HashIndex
hi = HashIndex(objects, ['attr1', 'attr2', 'attr3'])
hi.find(                                                # find objects
    match={'attr1': a, 'attr2': [b, c]},                # where attr1 == a and attr2 in [b, c]
    exclude={'attr3': d}                                # and attr3 != d
)
```

Any Python object can go in a HashIndex: class instances, namedtuples, dicts, strings, floats, ints, etc.

Nested attributes and derived attributes can be indexed using custom functions. See examples below.

There are two container classes available.
 - HashIndex: allows addition / removal of objects after creation
 - FrozenHashIndex: much faster performance, but objects cannot be added / removed after creation

____

## Examples

### Find dicts by attribute

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

### Nested attributes

```
from hashindex import FrozenHashIndex

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
    
hi = FrozenHashIndex(objects, ['size', has_cheese])

# returns orders 1, 2 and 4
hi.find({has_cheese: True})  
```

### String objects

```
from hashindex import FrozenHashIndex

objects = ['one', 'two', 'three']

def e_count(obj):
    return obj.count('e')

hi = FrozenHashIndex(objects, [e_count, len])
hi.find({len: 3})       # returns ['one', 'two']
hi.find({e_count: 2})  # returns ['three']
```

____

## Performance

### FrozenHashIndex



### HashIndex



____

## How it works

At a high level, you can think of each attribute index as a dict of set of object IDs. Each attribute lookup
returns a set of object IDs. Then union / intersection / difference operations are performed on the results of those
lookups to find the object IDs matching the query constraints. Finally, the object corresponding to each ID is returned. 

In practice, HashIndex uses specialized data structures to achieve this in a fast, memory-efficient way.

[Data structures](docs/data_structures.md)

____

## Updating indexed objects

HashIndex and FrozenHashIndex assume that the indexed attributes of their objects do not change.

⚠ ️ Breaking this assumption will cause inaccurate results or exceptions.

If you need to change an indexed attribute of an object, just remove it, apply the change, and add it back. 

#### This works
```
obj = {'attr': 1}
hi = HashIndex([obj], on=['attr'])
hi.remove(obj)
obj['attr'] = 2
hi.add(obj)
```

#### This will break index functions
```
obj = {'attr': 1}
hi = HashIndex([obj], on=['attr'])
obj.attr = some_other_thing   # don't do this
```

____

## API

WIP.

### Init

```
HashIndex(
        objs: Optional[Iterable[Any]] = None,
        on: List[str, Any] = None
)
```


### add()

```
add(obj:Any)
```

 - The objects do not need to be hashable. 
 - The attributes must be hashable.
 - If an object is missing an attribute, it will be indexed with a `None` value for that attribute.

____

## FrozenHashIndex Methods

### 

____
