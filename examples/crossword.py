"""
WIP -- may not finish this any time soon.

Making a demo of a crossword helper API.
"""

import flask
import pickle
import sys

from hashbox import HashBox


def serve():
    pass


def build():
    pass


def print_usage():
    print(
        'Usage: \ncrossword.py serve \ncrossword.py build \n"serve" runs the server, "build" builds the HashBox.'
    )


def main(arg):
    if arg == "build":
        build()
    elif arg == "serve":
        serve()
    else:
        print_usage()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_usage()
    main(sys.argv[1])
