# HashIndex

Find Python objects by exact match on their attributes.

`pip install hashindex`

### Project status

Beta, it probably works but I wouldn't put it in prod yet.

### Example

Find objects that have size "large", shape "circle" or "square", where the color is not "red".

```
from hashindex import HashIndex

hi = HashIndex(['size', 'color', 'shape'])
for obj in my_objects:
    hi.add(obj)
hi.find(match={'size': 'large', 'shape': ['circle', 'square']}, exclude={'color': 'red'})
```

[See docs for more.](https://pypi.org/project/hashindex/)

### Advantages

 * Works on your existing Python objects.
 * Objects are referenced, not copied.
 * Find operations are dict-speed. Remove and update are constant-time.

### Limitations

 * Supports exact-value lookups only. Use [RangeIndex](https://github.com/manimino/rangeindex/) if you need other comparisons.
 * Indexed values must be hashable.
 * Not thread-safe.

### Performance

