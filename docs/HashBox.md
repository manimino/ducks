# Table of Contents

* [hashbox.mutable.main](#hashbox.mutable.main)
  * [HashBox](#hashbox.mutable.main.HashBox)
    * [add](#hashbox.mutable.main.HashBox.add)
    * [remove](#hashbox.mutable.main.HashBox.remove)
    * [get\_values](#hashbox.mutable.main.HashBox.get_values)

<a id="hashbox.mutable.main"></a>

# hashbox.mutable.main

<a id="hashbox.mutable.main.HashBox"></a>

## HashBox Objects

```python
class HashBox()
```

<a id="hashbox.mutable.main.HashBox.add"></a>

#### add

```python
def add(obj: Any)
```

Add the object, evaluating any attributes and storing the results.

<a id="hashbox.mutable.main.HashBox.remove"></a>

#### remove

```python
def remove(obj: Any)
```

Remove the object. Raises KeyError if not present.

<a id="hashbox.mutable.main.HashBox.get_values"></a>

#### get\_values

```python
def get_values(attr: Union[str, Callable]) -> Set
```

Get the unique values we have for the given attribute. Useful for deciding what to find() on.

**Arguments**:

- `attr` - The attribute to get values for.
  

**Returns**:

  Set of all unique values for this attribute.

