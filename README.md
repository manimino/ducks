[![tests Actions Status](https://github.com/manimino/ducks/workflows/tests/badge.svg)](https://github.com/manimino/ducks/actions)
[![Coverage - 100%](https://img.shields.io/static/v1?label=Coverage&message=100%&color=2ea44f)](test/cov.txt)
[![license - MIT](https://img.shields.io/static/v1?label=license&message=MIT&color=2ea44f)](/LICENSE)
![python - 3.7+](https://img.shields.io/static/v1?label=python&message=3.7%2B&color=2ea44f)

# ducks 🦆

Provides Dex, a Python container for indexing objects of any type.

#### Install

```
pip install ducks
```

#### Usage

```
from ducks import Dex

objects = [{'x': 4, 'y': 1}, {'x': 6, 'y': 2}, {'x': 8, 'y': 5}]

# Create a Dex containing the objects. Index on x and y.
dex = Dex(objects, ['x', 'y'])  

# find the ones you want
dex[{                           # find objects
    'x': {'>': 5, '<': 10},     # where x is between 5 and 10
    'y': {'in': [1, 2, 3]}      # and y is 1, 2, or 3
}]
# result: [{'x': 6, 'y': 2}]
```

Valid operators are ==, !=, <, <=, >, >=, in, not in. 

#### Docs

There's more to `ducks` than making a `Dex` of `dict`s. [See the docs.](https://ducks.readthedocs.io)
