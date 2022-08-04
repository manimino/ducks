# Table of Contents

* [hashbox.frozen.main](#hashbox.frozen.main)
  * [FrozenHashBox](#hashbox.frozen.main.FrozenHashBox)
    * [\_\_init\_\_](#hashbox.frozen.main.FrozenHashBox.__init__)
    * [find](#hashbox.frozen.main.FrozenHashBox.find)
    * [get\_values](#hashbox.frozen.main.FrozenHashBox.get_values)

<a id="hashbox.frozen.main"></a>

# hashbox.frozen.main

<a id="hashbox.frozen.main.FrozenHashBox"></a>

## FrozenHashBox Objects

```python
class FrozenHashBox()
```

Like HashBox, but faster, more memory-efficient, and immutable. Great for making APIs to serve static data.

<a id="hashbox.frozen.main.FrozenHashBox.__init__"></a>

#### \_\_init\_\_

```python
def __init__(objs: Iterable[Any], on: Iterable[Union[str, Callable]])
```

Create a FrozenHashBox containing the objs, queryable by the 'on' attributes.

**Arguments**:

- `objs` - The objects that FrozenHashBox will contain.
  Objects do not need to be hashable, any object works.
  
- `on` - The attributes that FrozenHashBox will build indices on.
  Must contain at least one.
  
  It's OK if the objects in "objs" are missing some or all of the attributes in "on". They will still be
  stored, and can found with find(), e.g. when matching all objects or objects missing an attribute.
  
  For the objects that do contain the attributes on "on", those attribute values must be hashable.

<a id="hashbox.frozen.main.FrozenHashBox.find"></a>

#### find

```python
def find(
    match: Optional[Dict[Union[str, Callable], Union[Hashable,
                                                     List[Hashable]]]] = None,
    exclude: Optional[Dict[Union[str, Callable], Union[Hashable,
                                                       List[Hashable]]]] = None
) -> np.ndarray
```

Find objects in the FrozenHashBox that satisfy the match and exclude constraints.

**Arguments**:

- `match` - Specifies the subset of objects that match.
  Attribute is a string or Callable. Must be one of the attributes specified in the constructor.
  Value is any hashable type, or it can be a list of values.
  
  There is an implicit "and" between elements. match={'a': 1, 'b': 2} matches all objects with 'a'==1
  and 'b'==2.
  
  When the value is a list, all objects containing any value in the list will match. `{'a': [1, 2, 3]}`
  matches any object with an 'a' of 1, 2, or 3. Read it as ('a' in [1, 2, 3]).
  
  If an attribute value is None, objects that are missing the attribute will be matched, as well as
  any objects that have the attribute equal to None.
  
  match=None means all objects will be matched.
  
- `exclude` - Specifies the subset of objects that do not match.
  
  excluding `{'a': 1, 'b': 2}` ensures that no objects with 'a'==1 will be in the output, and no
  objects with 'b'==2 will be in the output. Read it as ('a' != 1 and 'b' != 2).
  
  excluding `{'a': [1, 2, 3]}` ensures that no objects with 'a' equal to 1, 2, or 3 will be in the output.
  Read it as ('a' not in [1, 2, 3]).
  

**Returns**:

  Numpy array of objects matching the constraints.

<a id="hashbox.frozen.main.FrozenHashBox.get_values"></a>

#### get\_values

```python
def get_values(attr: Union[str, Callable]) -> Set
```

Get the unique values we have for the given attribute. Useful for deciding what to find() on.

**Arguments**:

- `attr` - The attribute to get values for.
  

**Returns**:

  Set of all unique values for this attribute.

