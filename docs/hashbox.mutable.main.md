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
