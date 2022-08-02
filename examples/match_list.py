"""
Everyone ordered hash browns at Waffle House. Good choice.
Which orders match our search criteria?

Demonstrates use of lists for matching attribute values.
"""


from hashbox import HashBox

objects = [
    {"order": 1, "size": "regular", "topping": "smothered"},
    {"order": 2, "size": "regular", "topping": "diced"},
    {"order": 3, "size": "large", "topping": "covered"},
    {"order": 4, "size": "triple", "topping": "chunked"},
]

hb = HashBox(objects, on=["size", "topping"])

hb.find(
    match={
        "size": ["regular", "large"]
    },  # match anything with size in ['regular', 'large']
    exclude={"topping": "diced"},  # exclude where topping is 'diced'
)  # result: orders 1 and 3

hb.find(
    match={},  # match all objects
    exclude={"size": ["regular", "large"]},  # where size is not in ['regular', 'large']
)  # result: order 4
