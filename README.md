# HashIndex

[![tests Actions Status](https://github.com/manimino/hashindex/workflows/tests/badge.svg)](https://github.com/manimino/hashindex/actions)

Find Python objects by exact match on their attributes.

`pip install hashindex`

### Project status

Beta, it probably works, but I wouldn't put it in prod yet.

### Examples

Find objects that have size "large", shape "circle" or "square", where the color is not "red".

```
from hashindex import HashIndex

hi = HashIndex(my_objects, ['size', 'color', 'shape'])
hi.find(
    match={
        'size': 'large', 
        'shape': ['circle', 'square']
    }, 
    exclude={
        'color': 'red'
    })
```

You can also index on functions of objects.

```
def has_e(obj):
    return 'e' in obj

objects = ['one', 'two', 'three']
hi = HashIndex(objects, [has_e, len])
hi.find({len, 3})       # returns ['one', 'two']
hi.find({has_e, True})  # returns ['one', 'three']
```

More examples:
- FizzBuzz 
- Wordle solver

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

Pretty good.


### 

*Attributes, attributes, Can help you organize*

*A group that's too diverse and dense*

*into smaller groups that make more sense*

*So finally, everything computes*

*Thanks to attributes*

-- Peg and Cat