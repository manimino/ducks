<!-- markdownlint-disable -->

<a href="../hashbox/mutable/main.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `hashbox.mutable.main`






---

<a href="../hashbox/mutable/main.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `HashBox`




<a href="../hashbox/mutable/main.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    objs: Optional[Iterable[Any]] = None,
    on: Iterable[Union[str, Callable]] = None
)
```








---

<a href="../hashbox/mutable/main.py#L131"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add`

```python
add(obj: Any)
```

Add the object, evaluating any attributes and storing the results. 

---

<a href="../hashbox/mutable/main.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find`

```python
find(
    match: Optional[Dict[Union[str, Callable], Any]] = None,
    exclude: Optional[Dict[Union[str, Callable], Any]] = None
) → List
```

Find objects in the HashBox that satisfy the match and exclude constraints. 



**Args:**
 
 - <b>`match`</b>:  Specifies the subset of objects that match.  If unspecified, all objects will match. 

 Specify a dictionary of {attribute﹕ value} to constrain the objects that match. 

 The attribute is a string or Callable. Must be one of the attributes specified in the constructor. 

 Value can be any of the following.  * A single hashable value, which will match all objects with that value for the attribute.  * A list of hashable values, which matches each object having any of the values for the attribute.  * hashbox.ANY, which matches all objects having the attribute.  


 - <b>`exclude`</b>:  Specifies the subset of objects that do not match.  If unspecified, no objects will be excluded. 

 Specify a dictionary of {attribute﹕ value}  to exclude objects from the results. 

 Value can be any of the following.  * A single hashable value, which will exclude all objects with that value for the attribute.  * A list of hashable values, which excludes each object having any of the values for the attribute.  * hashbox.ANY, which excludes all objects having the attribute. 



**Returns:**
 List of objects matching the constraints. 

---

<a href="../hashbox/mutable/main.py#L148"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="../hashbox/mutable/main.py#L138"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove`

```python
remove(obj: Any)
```

Remove the object. Raises KeyError if not present. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
