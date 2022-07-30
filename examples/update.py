from hashbox import HashBox


class Changey:
    """A class containing a variable _n that changes. On change, it will update each HashBox in its listeners."""

    def __init__(self, n):
        self._n = n
        self.listeners = []

    def add_listener(self, f: HashBox):
        self.listeners.append(f)

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, new_n):
        for f in self.listeners:
            f.remove(self)
        self._n = new_n
        for f in self.listeners:
            f.add(self)


def main():
    objs = [Changey(1) for _ in range(10)]
    f = HashBox(objs, ["n"])
    for obj in objs:
        obj.add_listener(f)
    assert len(f.find({"n": 1})) == 10

    # change an object
    objs[0].n = 2

    # see that changes are propagated to HashBox
    assert len(f.find({"n": 1})) == 9
    assert len(f.find({"n": 2})) == 1


if __name__ == "__main__":
    main()
