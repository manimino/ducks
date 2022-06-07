# MatchIndex

Find Python objects by matching their attributes.

`pip install matchindex`

Find objects that have size "large", shape "circle" or "square", where the color is not "red".

```
from matchindex import MatchIndex

mi = MatchIndex(['size', 'color', 'shape'])
for obj in my_objects:
    mi.add(obj)
mi.find(match={'size': 'large', 'shape': ['circle', 'square']}, exclude={'color': 'red'})
```

#### Advantages

 * Works on your existing Python objects. Just add them to the index.
 * RAM-efficient. Objects are stored by reference in dynamically chosen containers.
 * Unlike a DB, there's no need for schemas, serialization, etc. 
 * Finds are dict-speed.

#### Limitations

MatchIndex performs exact-value lookups only. It does not perform range queries or wildcard matching; consider 
heavier solutions like pandas or a DB if you need those.

Indexed values must be hashable.

MatchIndex is not thread-safe.