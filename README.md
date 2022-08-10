# FilterBox

Container for finding Python objects.

Stores objects in hashtables by attribute value, so finds are very fast. 

[Finding objects using FilterBox can be 5-10x faster than SQLite.](https://github.com/manimino/filterbox/blob/main/examples/perf_demo.ipynb)

[![tests Actions Status](https://github.com/manimino/filterbox/workflows/tests/badge.svg)](https://github.com/manimino/filterbox/actions)
[![Coverage - 100%](https://img.shields.io/static/v1?label=Coverage&message=100%&color=2ea44f)](test/cov.txt)
[![license - MIT](https://img.shields.io/static/v1?label=license&message=MIT&color=2ea44f)](/LICENSE)
![python - 3.7+](https://img.shields.io/static/v1?label=python&message=3.7%2B&color=2ea44f)


### Install

```
pip install filterbox
```

### Usage

Find a good day for flying a kite. It needs to have sunny skies and a wind speed between 5 and 10.

```
from filterbox import FilterBox

days = [
    {'day': 'Saturday', 'sky': 'sunny', 'wind_speed': 1},
    {'day': 'Sunday', 'sky': 'rainy', 'wind_speed': 3},
    {'day': 'Monday', 'sky': 'sunny', 'wind_speed': 7},
    {'day': 'Tuesday', 'sky': 'rainy', 'wind_speed': 9},
    {'day': 'Wednesday', 'sky': 'sunny', 'wind_speed': 25}
]

# make a FilterBox
fb = FilterBox(               # make a FilterBox
    days,                     # add objects of any Python type
    on=['sky', 'wind_speed']  # attributes to find by
)

fb.find({'sky': 'sunny', 'wind_speed': {'>=': 5, '<=': 10}})  
# result: [{'day': 'Monday', 'sky': 'sunny', 'wind_speed': 7}]
```

You can also find objects by functions evaluated on the object. 

Find palindromes of length 5 or 7:
```
from filterbox import FilterBox
strings = ['bob', 'fives', 'kayak', 'stats', 'pullup', 'racecar']

def is_palindrome(s):
    return s == s[::-1]

fb = FilterBox(strings, [is_palindrome, len])
fb.find({is_palindrome: True, len: {'in': [5, 7]}})  
# result: ['kayak', 'racecar', 'stats']
```

Functions are evaluated only once, when the object is added to the FilterBox. 

### Classes

 - `FilterBox` - can add, remove, and update objects after creation.
 - `ConcurrentFilterBox` - Thread-safe version of FilterBox. 
 - `FrozenFilterBox` - Cannot be changed after creation. Fastest finds, lower memory usage, and thread-safe.

## More Examples

Expand for sample code.

<details>
<summary>Exclude values</summary>
<br>

`find()` takes two arguments, `match` and `exclude`. The examples up to this point have used `match` only, but
`exclude` works the same way.


```
from filterbox import FilterBox

objects = [
    {'item': 1, 'size': 10, 'flavor': 'melon'}, 
    {'item': 2, 'size': 10, 'flavor': 'lychee'}, 
    {'item': 3, 'size': 20, 'flavor': 'peach'},
    {'item': 4, 'size': 30, 'flavor': 'apple'}
]

fb = FilterBox(objects, on=['size', 'flavor'])

fb.find(
    match={'size': {'<': 30}},                       # match anything with size < 30
    exclude={'flavor': {'in': ['lychee', 'peach']}}  # where flavor is not in ['lychee', 'peach']
)  
# result: [{'item': 1, 'size': 10, 'flavor': 'melon'}]
```

If `match` is unspecified, all objects will match, which allows filtering solely by `exclude`. Try removing 
the `match` line in the example above.

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
fb.find({get_nested: 4})  
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

fb.find({'a': ANY})          # result: [{'a': 1}, {'a': 2}]
fb.find({get_a: ANY})        # result: [{'a': 1}, {'a': 2}]
fb.find(exclude={'a': ANY})  # result: [{}]
```
</details>

### Recipes
 
 - [Auto-updating](https://github.com/manimino/filterbox/blob/main/examples/update.py) - Keep FilterBox updated when objects change
 - [Wordle solver](https://github.com/manimino/filterbox/blob/main/examples/wordle.ipynb) - Solve string matching problems faster than regex
 - [Collision detection](https://github.com/manimino/filterbox/blob/main/examples/collision.py) - Find objects based on type and proximity (grid-based)
 - [Percentiles](https://github.com/manimino/filterbox/blob/main/examples/percentile.py) - Find by percentile (median, p99, etc.)

____

## How it works

For each attribute in the FilterBox, it holds a dict that maps every unique value to the set of objects with that value. 

This is the rough idea of the data structure: 
```
class FilterBox:
    indices = {
        'attribute1': {val1: set(some_obj_ids), val2: set(other_obj_ids)},
        'attribute2': {val3: set(some_obj_ids), val4: set(other_obj_ids)},
    }
    'obj_map': {obj_ids: objects}
}
```

During `find()`, the object ID sets matching each query value are retrieved. Then set operations like `union`, 
`intersect`, and `difference` are applied to get the matching object IDs. Finally, the object IDs are converted
to objects and returned.

In practice, FilterBox and FrozenFilterBox have more complexity, as they are optimized to have much better
memory usage and speed than a naive implementation. 

See the "how it works" pages for more detail:
 - [How FilterBox works](filterbox/mutable/how_it_works.md)
 - [How ConcurrentFilterBox works](filterbox/concurrent/how_it_works.md)
 - [How FrozenFilterBox works](filterbox/frozen/how_it_works.md)

### API Reference:

 - [FilterBox API](https://filterbox.readthedocs.io/en/latest/filterbox.mutable.html#filterbox.mutable.main.FilterBox)
 - [ConcurrentFilterBox API](https://filterbox.readthedocs.io/en/latest/filterbox.concurrent.html#filterbox.concurrent.main.ConcurrentFilterBox)
 - [FrozenFilterBox API](https://filterbox.readthedocs.io/en/latest/filterbox.frozen.html#filterbox.frozen.main.FrozenFilterBox)

### Related projects

FilterBox is a type of inverted index. It is optimized for its goal of finding in-memory Python objects.

Other Python inverted index implementations are aimed at things like [vector search](https://pypi.org/project/rii/) and
[finding documents by words](https://pypi.org/project/nltk/). Outside of Python, ElasticSearch is a popular inverted
index search tool. Each of these has goals outside of FilterBox's niche; there are no plans to expand FilterBox towards
these functions.

____
