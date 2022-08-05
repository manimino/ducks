# Table of Contents

* [filterbox.frozen.main](#filterbox.frozen.main)
  * [FrozenFilterBox](#filterbox.frozen.main.FrozenFilterBox)
    * [\_\_init\_\_](#filterbox.frozen.main.FrozenFilterBox.__init__)
    * [find](#filterbox.frozen.main.FrozenFilterBox.find)
    * [get\_values](#filterbox.frozen.main.FrozenFilterBox.get_values)

<a id="filterbox.frozen.main"></a>

# filterbox.frozen.main

<a id="filterbox.frozen.main.FrozenFilterBox"></a>

## FrozenFilterBox Objects

```python
class FrozenFilterBox()
```

A much faster FilterBox that lacks the ability to add or remove objects.

<a id="filterbox.frozen.main.FrozenFilterBox.__init__"></a>

#### \_\_init\_\_

```python
def __init__(objs: Iterable[Any], on: Iterable[Union[str, Callable]])
```

Create a FrozenFilterBox containing the objs, queryable by the 'on' attributes.

**Arguments**:

- `objs` _Any iterable containing any types_ - The objects that FrozenFilterBox will contain.
  Must contain at least one object. Objects do not need to be hashable, any object works.
  
- `on` _Iterable of attributes_ - The attributes that FrozenFilterBox will build indices on.
  Must contain at least one.
  
  Objects in obj do not need to have all of the attributes in 'on'.

<a id="filterbox.frozen.main.FrozenFilterBox.find"></a>

#### find

```python
def find(
    match: Optional[Dict[Union[str, Callable], Union[Hashable,
                                                     List[Hashable]]]] = None,
    exclude: Optional[Dict[Union[str, Callable], Union[Hashable,
                                                       List[Hashable]]]] = None
) -> np.ndarray
```

Find objects in the FrozenFilterBox that satisfy the match and exclude constraints.

**Arguments**:

- `match` _Dict of {attribute: value}, or None_ - Specifies the subset of objects that match.
  Attribute is a string or Callable. Must be one of the attributes specified in the constructor.
  Value is any hashable type, or it can be a list of values.
  
  There is an implicit "and" between elements.
- `Example` - match={'a': 1, 'b': 2} matches all objects with 'a'==1 and 'b'==2.
  
  When the value is a list, all objects containing any value in the list will match.
- `Example` - {'a': [1, 2, 3]} matches any object with an 'a' of 1, 2, or 3.
  
  If an attribute value is None, objects that are missing the attribute will be matched, as well as
  any objects that have the attribute equal to None.
  
  match=None means all objects will be matched.
  
- `exclude` _Dict of {attribute: value}, or None_ - Specifies the subset of objects that do not match.
- `exclude={'a'` - 1, 'b': 2} ensures that no objects with 'a'==1 will be in the output, and no
  objects with 'b'==2 will be in the output.
  
  You can also read this as "a != 1 and b != 2".
  
- `exclude={'a'` - [1, 2, 3]} ensures that no objects with 'a' equal to 1, 2, or 3 will be in the output.
  

**Returns**:

  Numpy array of objects matching the constraints.
  

**Example**:

  find(
- `match={'a'` - 1, 'b': [1, 2, 3]},
- `exclude={'c'` - 1, 'd': 1}
  )
  This is analogous to:
  filter(
  lambda obj: obj.a == 1 and obj.b in [1, 2, 3] and obj.c != 1 and obj.d != 1,
  objects
  )

<a id="filterbox.frozen.main.FrozenFilterBox.get_values"></a>

#### get\_values

```python
def get_values(attr: Union[str, Callable]) -> Set
```

Get the unique values we have for the given attribute. Useful for deciding what to find() on.

