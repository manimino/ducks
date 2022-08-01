"""
Are any mice in range of a cat? Let's find out.
We don't want to do all n_cats * n_mice comparisons, so we'll use Filtered to find ones in the same or adjacent
grid squares.
"""

from filtered import Filtered


class Cat:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y


class Mouse:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y


def in_range(mouse: Mouse, cat: Cat, radius: float = 1.0):
    return ((mouse.x - cat.x) ** 2 + (mouse.y - cat.y) ** 2) ** 0.5 < radius


def main():
    mice = [
        Mouse("Mickey", 0.3, 0.5),
        Mouse("Minnie", 0.3, 0.6),
        Mouse("Hannah", 5.3, 5.5),
        Mouse("Jerry", 5.1, 1.5),
    ]
    cats = [
        Cat("Tab", 4.0, 3.6),
        Cat("Tom", 4.9, 1.1),
        Cat("Hobbes", 2.2, 2.2),
        Cat("Garfield", 3.6, 1.9),
    ]

    def grid_x(obj):
        return int(obj.x)

    def grid_y(obj):
        return int(obj.y)

    f = Filtered(mice + cats, [grid_x, grid_y, type])
    for m in mice:
        # only search the grid squares near this mouse, and only look at Cats
        nearby_cats = f.find(
            {
                grid_x: [grid_x(m), grid_x(m) - 1, grid_x(m) + 1],
                grid_y: [grid_y(m), grid_y(m) - 1, grid_y(m) + 1],
                type: Cat,
            }
        )
        for c in nearby_cats:
            if in_range(m, c):
                print(f"Mouse {m.name} is in range of cat {c.name}!")


if __name__ == "__main__":
    main()
