# HashIndex

Find Python objects by exact match on their attributes.

`pip install hashindex`

### Example

Find objects that have size "large", shape "circle" or "square", where the color is not "red".

```
from hashindex import HashIndex

mi = HashIndex(['size', 'color', 'shape'])
for obj in my_objects:
    mi.add(obj)
mi.find(match={'size': 'large', 'shape': ['circle', 'square']}, exclude={'color': 'red'})
```

[See docs for more.]()

### Advantages

 * Works on your existing Python objects.
 * Unlike a DB, there's no need for schemas, serialization, syncing, etc.
 * RAM-efficient, by Python standards. Objects are stored by reference in dynamically chosen containers.
 * Find operations are dict-speed. Remove and update are constant-time.

### Limitations

HashIndex performs exact-value lookups only. It does not perform range queries or wildcard matching; consider 
heavier solutions like pandas or a DB if you need those.

Indexed values must be hashable.

HashIndex is not thread-safe.