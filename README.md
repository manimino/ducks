# HashBox

Put your Python objects in the HashBox. 

Query on their attributes in O(1). 

Supports O(1) removal and update.

`pip install hashbox`

### Basic Usage
```
box = HashBox(['shape', 'color'])
for item in items:
    box.add(item)
box.find(having={'shape': 'circle'}, excluding: {'color': 'red'})
```

That returns all the items where item.shape is 'circle' and item.color is not 'red'.

### Full example

Define a dataclass:
```
@dataclass
class Pokemon:
    name: str
    type1: str
    type2: Optional[str]
```

Make some objects, put them in the HashBox:
```
from hashbox import HashBox

zapdos = Pokemon('Zapdos', 'Electric', 'Flying')
pikachu_1 = Pokemon('Pikachu', 'Electric', None)
pikachu_2 = Pokemon('Pikachu', 'Electric', None)
eevee = Pokemon('Eevee', 'Normal', None)

box = HashBox(get_attribs(Pokemon))
box.add(zapdos)
box.add(pikachu_1)
box.add(pikachu_2)
box.add(eevee)
```

Find matching objects:
```
box.find(having={'name': 'Pikachu'})              # Finds two Pikachus
box.find(having=None, excluding={'type2': None})  # Finds Zapdos
```

Update an object:
```
# What?! Eevee is evolving!
box.update(eevee, {'name': 'Jolteon', 'type1': 'Electric', 'type2': None})
box.find({'name': 'Eevee'})    # No results
box.find({'name': 'Jolteon'})  # Finds Jolteon
```

Delete an object:
```
box.delete(pikachu1)
box.find(having={'name': 'Pikachu'})  # Finds one Pikachu
```

### Performance Numbers

HashBox is faster than O(n) search once you have about 1000 items.

Each index costs 100 ~ 300 bytes per item per index, depending on density.
So indexing 10 different attributes of 1 million items = 10*1M*100 = 1GB.

### Alternatives

Hashbox does exact-value lookups only.

If you need range queries, string matching, and so on, consider heavier solutions like sqlite or pandas.
