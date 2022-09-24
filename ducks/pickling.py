import pickle  # nosec
from typing import Union

from ducks.concurrent.main import ConcurrentDex
from ducks.concurrent.main import load as c_load
from ducks.concurrent.main import save as c_save
from ducks.frozen.main import FrozenDex
from ducks.frozen.main import load as f_load
from ducks.frozen.main import save as f_save
from ducks.mutable.main import Dex
from ducks.mutable.main import load as m_load
from ducks.mutable.main import save as m_save


def save(box: Union[Dex, FrozenDex, ConcurrentDex], filepath: str):
    """Save a Dex, FrozenDex, or ConcurrentDex to a file."""
    if type(box) is Dex:
        m_save(box, filepath)
    if type(box) is FrozenDex:
        f_save(box, filepath)
    if type(box) is ConcurrentDex:
        c_save(box, filepath)


def load(filepath: str) -> Union[Dex, FrozenDex, ConcurrentDex]:
    """Load a Dex, FrozenDex, or ConcurrentDex from a pickle file."""
    with open(filepath, "rb") as fh:
        saved = pickle.load(fh)  # nosec
        if isinstance(saved, FrozenDex):
            f_load(saved)  # mutates saved
            return saved
        elif "priority" in saved:
            return c_load(saved)
        else:
            return m_load(saved)
