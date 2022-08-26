[![tests Actions Status](https://github.com/manimino/ducks/workflows/tests/badge.svg)](https://github.com/manimino/ducks/actions)
[![Coverage - 100%](https://img.shields.io/static/v1?label=Coverage&message=100%&color=2ea44f)](test/cov.txt)
[![license - MIT](https://img.shields.io/static/v1?label=license&message=MIT&color=2ea44f)](/LICENSE)
![python - 3.7+](https://img.shields.io/static/v1?label=python&message=3.7%2B&color=2ea44f)

# ducks

Provides Dex, a Python container for indexing objects of any type.

#### Install: 

```
pip install ducks
```

#### Usage:
```
from ducks import Dex

objects = [{'x': 4, 'y': 1}, {'x': 6, 'y': 2}, {'x': 8, 'y': 5}]

# Create a Dex containing objects. Index on x and y.
dex = Dex(objects, ['x', 'y'])  

# find the ones you want
dex[{                           # find objects
    'x': {'>': 5, '<': 10},     # where x is between 5 and 10
    'y': {'in': [1, 2, 3]}      # and y is 1, 2, or 3
}]
# result: [{'x': 6, 'y': 2}]
```

Valid operators are ==, !=, <, <=, >, >=, in, not in. 

#### Is Dex a database?

No. But like a database, Dex uses B-tree indexes and uses them to find results very quickly. It does
not any do other database things like SQL, tables, etc. This keeps Dex simple, light, and performant.

#### Is Dex fast?

Yes. Here's how Dex compares to other object-finders on an example task.

![Example benchmark](examples/img/perf_bench.png)

[Benchmark code](examples/perf_demo.ipynb)

The closest thing to a Dex is an in-memory SQLite. While SQLite is a fantastic database, it requires
more overhead. As such, Dex is generally faster.

### Class APIs

There are three containers.
 - Dex: Can `add`, `remove`, and `update` objects after creation.
[API]((https://ducks.readthedocs.io/en/latest/ducks.mutable.html#ducks.mutable.main.Dex))
 - ConcurrentDex: Same as Dex, but thread-safe.
[API](https://ducks.readthedocs.io/en/latest/ducks.concurrent.html#ducks.concurrent.main.ConcurrentDex)
 - FrozenDex: Cannot be changed after creation, it's read-only. But it's super fast, and of course thread-safe.
[API](https://ducks.readthedocs.io/en/latest/ducks.frozen.html#ducks.frozen.main.FrozenDex)

All three can be pickled using the special functions `ducks.save(dex, file)` / `ducks.load(file)`. 


### Fancy Tricks

Expand for sample code.

<details>
<summary>Use functions of the object as attributes</summary>
<br />
You can also index on functions evaluated on the object, as if they were attributes.

Find palindromes of length 5 or 7:
```
from ducks import Dex
strings = ['bob', 'fives', 'kayak', 'stats', 'pullup', 'racecar']

# define a function that takes the object as input
def is_palindrome(s):
    return s == s[::-1]

dex = Dex(strings, [is_palindrome, len])
dex[{
    is_palindrome: True, 
    len: {'in': [5, 7]}
}]
# result: ['kayak', 'racecar', 'stats']
```

Functions are evaluated on the object when it is added to the Dex. 

</details>

<details>
<summary>Access nested data using functions</summary>
<br />
Use functions to get values from nested data structures.

```
from ducks import Dex

objs = [
    {'a': {'b': [1, 2, 3]}},
    {'a': {'b': [4, 5, 6]}}
]

def get_nested(obj):
    return obj['a']['b'][0]

dex = Dex(objs, [get_nested])
dex[{get_nested: 4}]
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
 - In functions, raise <code>MissingAttribute</code> to tell Dex the object is missing.

Example:
```
from ducks import Dex, ANY
from ducks.exceptions import MissingAttribute

objs = [{'a': 1}, {'a': 2}, {}]

def get_a(obj):
    try:
        return obj['a']
    except KeyError:
        raise MissingAttribute  # tell Dex this attribute is missing

dex = Dex(objs, ['a', get_a])

dex[{'a': ANY}]          # result: [{'a': 1}, {'a': 2}]
dex[{get_a: ANY}]        # result: [{'a': 1}, {'a': 2}]
dex[{'a': {'!=': ANY}}]  # result: [{}]
```

Note that `None` is treated as a normal value and is stored.
</details>


### Recipes
 
 - [Auto-updating](https://github.com/manimino/ducks/blob/main/examples/update.py) - Keep Dex updated when objects change
 - [Wordle solver](https://github.com/manimino/ducks/blob/main/examples/wordle.ipynb) - Solve string matching problems faster than regex
 - [Collision detection](https://github.com/manimino/ducks/blob/main/examples/collision.py) - Find objects based on type and proximity (grid-based)
 - [Percentiles](https://github.com/manimino/ducks/blob/main/examples/percentile.py) - Find by percentile (median, p99, etc.)


## How Dex works

For each attribute in the Dex, it holds a B-tree that maps every unique value to the set of objects with 
that value. 

This is a rough idea of the data structure: 
```
class Dex:
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

In practice, Dex and FrozenDex have a bit more to them, as they are optimized to have much better
memory usage and speed than a naive implementation. For example, FrozenDex uses an array-based tree structure.

See the "how it works" pages for more detail:
 - [How Dex works](ducks/mutable/how_it_works.md)
 - [How ConcurrentDex works](ducks/concurrent/how_it_works.md)
 - [How FrozenDex works](ducks/frozen/how_it_works.md)
