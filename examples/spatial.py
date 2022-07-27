"""
Are any mice in range of the cats? Let's find out
"""


class Cat:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Mouse:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def collide(m, p, radius=1.0):
    return ((m.x - p.x) ** 2 + (m.y - p.y) ** 2) ** 0.5 < radius


def main():
    pass


if __name__ == "__main__":
    main()
