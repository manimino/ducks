# MatchIndex

Put your Python objects in a MatchIndex. 

Find objects by their attributes in O(1). 

Supports O(1) removal and update.

`pip install matchindex`

### Example Usage

Find all objects where obj.shape is 'circle' or 'square' and obj.color is not 'red'.

```
mi = MatchIndex(['shape', 'color'])
for obj in objects:
    mi.add(obj)
mi.find(match={'shape': ['circle', 'square']}, exclude={'color': 'red'})
```

### Larger Example

Define a dataclass:
```
@dataclass
class Pokemon:
    name: str
    type1: str
    type2: Optional[str]
```

Make some objects, put them in the MatchIndex:
```
from matchindex import MatchIndex, get_attribs

zapdos = Pokemon('Zapdos', 'Electric', 'Flying')
pikachu_1 = Pokemon('Pikachu', 'Electric', None)
pikachu_2 = Pokemon('Pikachu', 'Electric', None)
eevee = Pokemon('Eevee', 'Normal', None)

mi = MatchIndex(get_attribs(Pokemon))
mi.add(zapdos)
mi.add(pikachu_1)
mi.add(pikachu_2)
mi.add(eevee)
```

Find matching objects:
```
mi.find(having={'name': 'Pikachu'})              # Finds two Pikachus
mi.find(having=None, excluding={'type2': None})  # Finds Zapdos
```

Update an object:
```
# What?! Eevee is evolving!
mi.update(eevee, {'name': 'Jolteon', 'type1': 'Electric', 'type2': None})
mi.find({'name': 'Eevee'})    # No results
mi.find({'name': 'Jolteon'})  # Finds Jolteon
```

Delete an object:
```
mi.delete(pikachu1)
mi.find(having={'name': 'Pikachu'})  # Finds the one remaining Pikachu
```

### Performance

Finding items in a MatchIndex is faster than doing a linear scan once you have about 1000 items.

RAM cost is about 100 bytes per item per index.

So, indexing 10 different attributes of 1 million items = (10 indexes * 1M items * 100 bytes) = about 1GB.

### Scope Declaration

MatchIndex does exact-value lookups only. 

If you need range queries, string matching, and so on, consider heavier solutions like sqlite or pandas.

It is not concurrent / thread-safe.