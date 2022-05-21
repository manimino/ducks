# MatchIndex

Put your Python objects in a MatchIndex. 

Find objects by their attributes in O(1). 

Remove or update an object in O(1).

`pip install matchindex`

### Example

Make some objects:
```
import dataclasses
from matchindex import MatchIndex
@dataclasses.dataclass
class Thing:
    shape: str
    color: str

objects = [
    Thing('square', 'green'),
    Thing('circle', 'green'),
    Thing('triangle', 'green'),
    Thing('square', 'red'),
    Thing('circle', 'red'),
    Thing('triangle', 'red'),
]
```

Make a MatchIndex on 'shape' and 'color'. Add the objects.
```
mi = MatchIndex(['shape', 'color'])
for obj in objects:
    mi.add(obj)
```

Find all the green objects: `mi.find(match={'color': 'green'}))`

Find all circles and squares that are not red:
`print(mi.find(match={'shape': ['circle', 'square']}, exclude={'color': 'red'}))`

### Larger Example

Define a dataclass:
```
@dataclasses.dataclass
class Pokemon:
    name: str
    type1: str
    type2: Optional[str]
```

Make some objects, put them in the MatchIndex:
```
from matchindex import MatchIndex, get_attributes

zapdos = Pokemon('Zapdos', 'Electric', 'Flying')
pikachu_1 = Pokemon('Pikachu', 'Electric', None)
pikachu_2 = Pokemon('Pikachu', 'Electric', None)
eevee = Pokemon('Eevee', 'Normal', None)

mi = MatchIndex(get_attributes(Pokemon))
mi.add(zapdos)
mi.add(pikachu_1)
mi.add(pikachu_2)
mi.add(eevee)
```

Find matching objects:
```
mi.find(match={'name': 'Pikachu'})  # Finds two Pikachus
mi.find(match=None, exclude={'name': ['Pikachu', 'Eevee']})  # Finds Zapdos
```

Update an object:
```
# What? Eevee is evolving!
mi.update(eevee, {'name': 'Jolteon', 'type1': 'Electric', 'type2': None})
mi.find({'name': 'Eevee'})    # No results
mi.find({'name': 'Jolteon'})  # Finds Jolteon
```

Delete an object:
```
mi.remove(pikachu_1)
mi.find({'name': 'Pikachu'})  # Finds the one remaining Pikachu
```

### Scope Declaration

MatchIndex does exact-value lookups only. Values must be hashable.

If you need range queries, string matching, and so on, consider heavier solutions like sqlite or pandas.

It is not concurrent / thread-safe.
