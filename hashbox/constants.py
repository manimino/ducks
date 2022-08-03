import sys

n_bits_signed = sys.hash_info.hash_bits - 1  # typically 64 bits
HASH_MIN = -(2 ** n_bits_signed)
HASH_MAX = 2 ** n_bits_signed - 1

SIZE_THRESH = 100

SET_SIZE_MIN = 10
TUPLE_SIZE_MAX = 100


class MatchAnything(set):
    pass


"""
ANY allows lookups like find({'attr': ANY}), which gives all objects that have an 'attr' attribute.

Why is this a set()?
We need a value that we can do "is" comparisons on, that will only be True
when it's literally this object. set() is a simple object that satisfies this property. 
"ANY is ANY" evaluates to True, but "set() is ANY" evaluates to False.
"""
ANY = MatchAnything()
