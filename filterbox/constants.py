SIZE_THRESH = 100

ARR_TYPE = "q"  # python array type meaning "int64": https://docs.python.org/3/library/array.html
SET_SIZE_MIN = 10
ARRAY_SIZE_MAX = 20


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

VALID_OPERATORS = [
    "==",
    "eq",
    "!=",
    "ne",
    "in",
    "not in",
    "<",
    "lt",
    "<=",
    "lte",
    "le",
    ">",
    "gt",
    ">=",
    "gte",
    "ge",
    "is",
    "is not",
]

OPERATOR_MAP = {
    "eq": "==",
    "lt": "<",
    "le": "<=",  # Python style <=
    "lte": "<=",  # ElasticSearch style <=
    "gt": ">",
    "ge": ">=",  # Python style >=
    "gte": ">=",  # ElasticSearch style >=
}

EXCLUDE_OPERATORS = {"not in": "in", "!=": "=="}
