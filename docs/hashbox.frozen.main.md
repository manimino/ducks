<!-- markdownlint-disable -->

<a href="../hashbox/frozen/main.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `hashbox.frozen.main`






---

<a href="../hashbox/frozen/main.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `FrozenHashBox`
Like HashBox, but faster, more memory-efficient, and immutable. Great for making APIs to serve static data. 

<a href="../hashbox/frozen/main.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(objs: Iterable[Any], on: Iterable[Union[str, Callable]])
```

Create a FrozenHashBox containing the objs, queryable by the 'on' attributes. 



**Args:**
 
 - <b>`objs`</b>:  The objects that FrozenHashBox will contain.  Objects do not need to be hashable, any object works. 


 - <b>`on`</b>:  The attributes that FrozenHashBox will build indices on.  Must contain at least one. 

It's OK if the objects in "objs" are missing some or all of the attributes in "on". They will still be stored, and can found with find(), e.g. when matching all objects or objects missing an attribute. 

For the objects that do contain the attributes on "on", those attribute values must be hashable. 




---

<a href="../hashbox/frozen/main.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find`

```python
find(
    match: Optional[Dict[Union[str, Callable], Union[Hashable, List[Hashable]]]] = None,
    exclude: Optional[Dict[Union[str, Callable], Union[Hashable, List[Hashable]]]] = None
) → ndarray
```

Find objects in the FrozenHashBox that satisfy the match and exclude constraints. 



**Args:**
 
 - <b>`match`</b>:  Specifies the subset of objects that match.  Attribute is a string or Callable. Must be one of the attributes specified in the constructor.  Value is any hashable type, or it can be a list of values. 


 - <b>`There is an implicit "and" between elements. match={'a'`</b>:  1, 'b': 2} matches all objects with 'a'==1 and 'b'==2. 


 - <b>`When the value is a list, all objects containing any value in the list will match. `{'a'`</b>:  [1, 2, 3]}` matches any object with an 'a' of 1, 2, or 3. Read it as ('a' in [1, 2, 3]). 

If an attribute value is None, objects that are missing the attribute will be matched, as well as any objects that have the attribute equal to None. 

match=None means all objects will be matched. 


 - <b>`exclude`</b>:  Specifies the subset of objects that do not match. 


 - <b>`Excluding `{'a'`</b>:  1, 'b': 2}` ensures that no objects with 'a'==1 will be in the output, and no objects with 'b'==2 will be in the output. Read it as ('a' != 1 and 'b' != 2). 


 - <b>`Excluding `{'a'`</b>:  [1, 2, 3]}` ensures that no objects with 'a' equal to 1, 2, or 3 will be in the output. Read it as ('a' not in [1, 2, 3]). 



**Returns:**
 Numpy array of objects matching the constraints. 

---

<a href="../hashbox/frozen/main.py#L128"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_values`

```python
get_values(attr: Union[str, Callable]) → Set
```

Get the unique values we have for the given attribute. Useful for deciding what to find() on. 



**Args:**
 
 - <b>`attr`</b>:  The attribute to get values for. 



**Returns:**
 Set of all unique values for this attribute. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
