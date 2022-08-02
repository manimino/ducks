"""
Suppose we have thousands of dicts, each containing different nested attributes.

We want to store them efficiently -- there should be no entry for "a" in the HashBox if the object
does not contain "a".
"""
from hashbox import HashBox
from hashbox.exceptions import MissingAttribute


def get_a0(obj):
    try:
        obj['a'][0]
    except KeyError:
        raise MissingAttribute  # Raising this tells HashBox not to store any value for this object.
    except IndexError:
        raise MissingAttribute
    except TypeError:
        raise MissingAttribute


def get_b0(obj):
    try:
        obj['b'][0]
    except KeyError:
        raise MissingAttribute
    except IndexError:
        raise MissingAttribute
    except TypeError:
        raise MissingAttribute


def main():
    data = [
        {'a': [1], 'b': [2]},
        {'b': [2]},  # AttributeError on get_a0
        {'a': []},   # IndexError on get_a0
        None         # TypeError on both
    ]
    hb = HashBox(data, [get_a0, get_b0])
    print('data length:', len(data))
    print('number of objects in HashBox:', len(hb))
    print('number of objects stored for attribute get_a0:', len(hb.indices[get_a0]))
    print('number of objects stored for attribute get_b0:', len(hb.indices[get_b0]))


if __name__ == '__main__':
    main()