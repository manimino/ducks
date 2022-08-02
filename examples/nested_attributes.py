from hashbox import HashBox


class Order:
    def __init__(self, num, size, toppings):
        self.num = num
        self.size = size
        self.toppings = toppings

    def __repr__(self):
        return f"order: {self.num}, size: '{self.size}', toppings: {self.toppings}"


objects = [
    Order(1, "regular", ["scattered", "smothered", "covered"]),
    Order(2, "large", ["scattered", "covered", "peppered"]),
    Order(3, "large", ["scattered", "diced", "chunked"]),
    Order(4, "triple", ["all the way"]),
]


def has_cheese(obj):
    return "covered" in obj.toppings or "all the way" in obj.toppings


hb = HashBox(objects, ["size", has_cheese])

# returns orders 1, 2 and 4
hb.find({has_cheese: True})
