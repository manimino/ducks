# Table of Contents

* [filterbox.mutable.main](#filterbox.mutable.main)
  * [FilterBox](#filterbox.mutable.main.FilterBox)
    * [add](#filterbox.mutable.main.FilterBox.add)
    * [remove](#filterbox.mutable.main.FilterBox.remove)
    * [get\_values](#filterbox.mutable.main.FilterBox.get_values)

<a id="filterbox.mutable.main"></a>

# filterbox.mutable.main

<a id="filterbox.mutable.main.FilterBox"></a>

## FilterBox Objects

```python
class FilterBox()
```

<a id="filterbox.mutable.main.FilterBox.add"></a>

#### add

```python
def add(obj: Any)
```

Add a new object, evaluating any attributes and storing the results.

<a id="filterbox.mutable.main.FilterBox.remove"></a>

#### remove

```python
def remove(obj: Any)
```

Remove an object. Raises KeyError if not present.

<a id="filterbox.mutable.main.FilterBox.get_values"></a>

#### get\_values

```python
def get_values(attr: Union[str, Callable]) -> Set
```

Get the unique values we have for the given attribute. Useful for deciding what to find() on.

