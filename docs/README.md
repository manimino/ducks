# TODO put this in the real docs

### Another Example

Define a dataclass:
```
@dataclasses.dataclass
class Pokemon:
    name: str
    type1: str
    type2: Optional[str]
```

Make some objects, put them in the HashIndex:
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
