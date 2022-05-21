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

Find all the squares: 
```
mi.find(match={'shape': 'square'})
# result:
# [Thing(shape='square', color='green'), Thing(shape='square', color='red')]
```


Find all circles and squares that are not red:
```
mi.find(match={'shape': ['circle', 'square']}, exclude={'color': 'red'})
# result: 
# [Thing(shape='circle', color='green'), Thing(shape='square', color='green')]
```

### Limitations

MatchIndex performs exact-value lookups only. It does not perform range queries or wildcard matching; consider 
heavier libraries like pandas or sqlite if you need those.

Indexed values must be hashable.

MatchIndex is not thread-safe.