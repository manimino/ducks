[![tests Actions Status](https://github.com/manimino/filterbox/workflows/tests/badge.svg)](https://github.com/manimino/filterbox/actions)
[![Coverage - 100%](https://img.shields.io/static/v1?label=Coverage&message=100%&color=2ea44f)](test/cov.txt)
[![license - MIT](https://img.shields.io/static/v1?label=license&message=MIT&color=2ea44f)](/LICENSE)
![python - 3.7+](https://img.shields.io/static/v1?label=python&message=3.7%2B&color=2ea44f)

# FilterBox

Container that stores objects in database-like indexes for fast lookup.

Install: `pip install filterbox`

Usage:
```
from filterbox import FilterBox
fb = FilterBox(your_objects, ['x', 'y'])  # create FilterBox containing objects, indexed on x and y
fb[{
    'x': {'>': 5, '<': 10},     # find objects where x is between 5 and 10
    'y': {'in': [1, 2, 3]}      # and y is 1, 2, or 3
}]
```

Valid operators are ==, !=, <, <=, >, >=, in, not in. 

#### Is FilterBox a database?

No. But like a database, FilterBox builds B-tree indexes and uses them to find results very quickly. It does
not any do other database things like SQL, tables, etc. This keeps FilterBox simple, light, and performant.

#### Is FilterBox fast?

Yes. Here's how FilterBox compares to other object-finders on an example task.

![Example benchmark](docs/perf_bench.png)

[Benchmark code](examples/perf_demo.ipynb)

The closest thing to a FilterBox is an in-memory SQLite. While SQLite is a fantastic database, it requires
more overhead. As such, FilterBox is generally faster.

### Example

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

fb = FilterBox(                     # make a FilterBox
     days,                     # add objects of any Python type
     on=['sky', 'wind_speed']  # what to index on
)

fb[{
    'sky': 'sunny', 
    'wind_speed': {'>': 5, '<': 10}
}]
# result: [{'day': 'Monday', 'sky': 'sunny', 'wind_speed': 7}]
```

`{'sky': 'sunny'}` is a shorthand for `{'sky': {'==': sunny}}`.

### Class APIs

There are three containers.
 - [FilterBox](https://filterbox.readthedocs.io/en/latest/filterbox.mutable.html#filterbox.mutable.main.FilterBox): 
Can add / remove items after creation.
 - [ConcurrentFilterBox](https://filterbox.readthedocs.io/en/latest/filterbox.concurrent.html#filterbox.concurrent.main.ConcurrentFilterBox): 
Same as FilterBox, but thread-safe.
 - [FrozenFilterBox](https://filterbox.readthedocs.io/en/latest/filterbox.frozen.html#filterbox.frozen.main.FrozenFilterBox):
Cannot add / remove items after creation, it's read-only. But it's super fast, and of course thread-safe.

All three can be pickled using the special functions `filterbox.save()` / `filterbox.load()`. 

### Part 2

[Readme Part 2](/README_part_2.md) has lots more examples, including handling of nested data and missing attributes.
