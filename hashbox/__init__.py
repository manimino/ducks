from hashbox.mutable.main import HashBox
from hashbox.frozen.main import FrozenHashBox

"""
ANY allows lookups like find({'attr': ANY}), which gives all objects that have an 'attr' attribute.

Why is this a set()?
We need a value that we can do "is" comparisons on, that will only be True
when it's literally this object. set() is a simple object that satisfies this property. 
"ANY is ANY" evaluates to True, but "set() is ANY" evaluates to False.
"""
ANY = set()
