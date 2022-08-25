[![tests Actions Status](https://github.com/manimino/filterbox/workflows/tests/badge.svg)](https://github.com/manimino/filterbox/actions)
[![Coverage - 100%](https://img.shields.io/static/v1?label=Coverage&message=100%&color=2ea44f)](test/cov.txt)
[![license - MIT](https://img.shields.io/static/v1?label=license&message=MIT&color=2ea44f)](/LICENSE)
![python - 3.7+](https://img.shields.io/static/v1?label=python&message=3.7%2B&color=2ea44f)

# FilterBox

Container that stores Python objects in database-like indexes for fast lookup.

#### Install: 

```
pip install filterbox
```

#### Usage:
```
from filterbox import FilterBox

objects = [{'x': 4, 'y': 1}, {'x': 6, 'y': 2}, {'x': 8, 'y': 5}]

# create a FilterBox containing objects, indexed on x and y
fb = FilterBox(objects, ['x', 'y'])  

# find the ones you want
fb[{
    'x': {'>': 5, '<': 10},     # find objects where x is between 5 and 10
    'y': {'in': [1, 2, 3]}      # and y is 1, 2, or 3
}]
# result: [{'x': 6, 'y': 2}]
```

Valid operators are ==, !=, <, <=, >, >=, in, not in. 

#### Is FilterBox a database?

No. But like a database, FilterBox builds B-tree indexes and uses them to find results very quickly. It does
not any do other database things like SQL, tables, etc. This keeps FilterBox simple, light, and performant.

#### Is FilterBox fast?

Yes. Here's how FilterBox compares to other object-finders on an example task.

![Example benchmark](examples/img/perf_bench.png)

[Benchmark code](examples/perf_demo.ipynb)

The closest thing to a FilterBox is an in-memory SQLite. While SQLite is a fantastic database, it requires
more overhead. As such, FilterBox is generally faster.

### Class APIs

There are three containers.
 - [FilterBox](https://filterbox.readthedocs.io/en/latest/filterbox.mutable.html#filterbox.mutable.main.FilterBox): 
Can `add`, `remove`, and `update` objects after creation.
 - [ConcurrentFilterBox](https://filterbox.readthedocs.io/en/latest/filterbox.concurrent.html#filterbox.concurrent.main.ConcurrentFilterBox): 
Same as FilterBox, but thread-safe.
 - [FrozenFilterBox](https://filterbox.readthedocs.io/en/latest/filterbox.frozen.html#filterbox.frozen.main.FrozenFilterBox):
Cannot be changed after creation, it's read-only. But it's super fast, and of course thread-safe.

All three can be pickled using the special functions `filterbox.save()` / `filterbox.load()`. 


### Fancy Tricks

Expand for sample code.

<details>
<summary>Use functions of the object as attributes</summary>
<br />
You can also index on functions evaluated on the object, as if they were attributes.

Find palindromes of length 5 or 7:
```
from filterbox import FilterBox
strings = ['bob', 'fives', 'kayak', 'stats', 'pullup', 'racecar']

# define a function that takes the object as input
def is_palindrome(s):
    return s == s[::-1]

fb = FilterBox(strings, [is_palindrome, len])
fb[{
    is_palindrome: True, 
    len: {'in': [5, 7]}
}]
# result: ['kayak', 'racecar', 'stats']
```

Functions are evaluated on the object when it is added to the FilterBox. 

</details>

<details>
<summary>Access nested data using functions</summary>
<br />
Use functions to get values from nested data structures.

```
from filterbox import FilterBox

objs = [
    {'a': {'b': [1, 2, 3]}},
    {'a': {'b': [4, 5, 6]}}
]

def get_nested(obj):
    return obj['a']['b'][0]

fb = FilterBox(objs, [get_nested])
fb[{get_nested: 4}]
# result: {'a': {'b': [4, 5, 6]}}
```
</details>

<details>
<summary>Handle missing attributes</summary>
<br />

Objects don't need to have every attribute.

 - Objects that are missing an attribute will not be stored under that attribute. This saves lots of memory.
 - To find all objects that have an attribute, match the special value <code>ANY</code>. 
 - To find objects missing the attribute, exclude <code>ANY</code>.
 - In functions, raise <code>MissingAttribute</code> to tell FilterBox the object is missing.

Example:
```
from filterbox import FilterBox, ANY
from filterbox.exceptions import MissingAttribute

objs = [{'a': 1}, {'a': 2}, {}]

def get_a(obj):
    try:
        return obj['a']
    except KeyError:
        raise MissingAttribute  # tell FilterBox this attribute is missing

fb = FilterBox(objs, ['a', get_a])

fb[{'a': ANY}]          # result: [{'a': 1}, {'a': 2}]
fb[{get_a: ANY}]        # result: [{'a': 1}, {'a': 2}]
fb[{'a': {'!=': ANY}}]  # result: [{}]
```

Note that `None` is treated as a normal value and is stored.
</details>


### Recipes
 
 - [Auto-updating](https://github.com/manimino/filterbox/blob/main/examples/update.py) - Keep FilterBox updated when objects change
 - [Wordle solver](https://github.com/manimino/filterbox/blob/main/examples/wordle.ipynb) - Solve string matching problems faster than regex
 - [Collision detection](https://github.com/manimino/filterbox/blob/main/examples/collision.py) - Find objects based on type and proximity (grid-based)
 - [Percentiles](https://github.com/manimino/filterbox/blob/main/examples/percentile.py) - Find by percentile (median, p99, etc.)


## How FilterBox works

For each attribute in the FilterBox, it holds a B-tree that maps every unique value to the set of objects with 
that value. 

This is a rough idea of the data structure: 
```
class FilterBox:
    indexes = {
        'attribute1': BTree({10: set(some_obj_ids), 20: set(other_obj_ids)}),
        'attribute2': BTree({'abc': set(some_obj_ids), 'def': set(other_obj_ids)}),
    }
    obj_map = {obj_ids: objects}
}
```

During a lookup, the object ID sets matching each query value are retrieved. Then set operations like `union`, 
`intersect`, and `difference` are applied to get the matching object IDs. Finally, the object IDs are converted
to objects and returned.

In practice, FilterBox and FrozenFilterBox have a bit more to them, as they are optimized to have much better
memory usage and speed than a naive implementation. 

See the "how it works" pages for more detail:
 - [How FilterBox works](filterbox/mutable/how_it_works.md)
 - [How ConcurrentFilterBox works](filterbox/concurrent/how_it_works.md)
 - [How FrozenFilterBox works](filterbox/frozen/how_it_works.md)
