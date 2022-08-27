# ducks 🦆

Index your Python objects for fast lookup by their attributes.

[![tests Actions Status](https://github.com/manimino/ducks/workflows/tests/badge.svg)](https://github.com/manimino/ducks/actions)
[![Coverage - 100%](https://img.shields.io/static/v1?label=Coverage&message=100%&color=2ea44f)](test/cov.txt)
[![license - MIT](https://img.shields.io/static/v1?label=license&message=MIT&color=2ea44f)](/LICENSE)
![python - 3.7+](https://img.shields.io/static/v1?label=python&message=3.7%2B&color=2ea44f)

### Install

```
pip install ducks
```

### Usage

The main container in ducks is called a Dex.

```
from ducks import Dex

objects = [
    {'x': 3, 'y': 'a'}, 
    {'x': 6, 'y': 'b'}, 
    {'x': 9, 'y': 'c'}
]

# Create a Dex containing the objects. 
# Index on x and y.
dex = Dex(objects, ['x', 'y'])  

# get objects
dex[{                        
    'x': {'>': 4, '<': 8},   # where 4 < x < 8
    'y': {'in': ['a', 'b']}  # and y is 'a' or 'b'
}]
# result: [{'x': 6, 'y': 'b'}]
```

 - The objects can be any Python type.
 - Supports ==, !=, in, not in, <, <=, >, >=.
 - Index using dict keys, object attributes, and custom functions.

### It's fast

<img src="https://github.com/manimino/ducks/blob/tweaks/docs/img/perf_bench.png" width="500" />

Ducks outperforms other data structures for finding Python objects.

### Docs

There's more to ducks than making a Dex of dicts. 

[Read the docs.](https://ducks.readthedocs.io)
