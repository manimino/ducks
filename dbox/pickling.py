import pickle
from typing import Union

from dbox.concurrent.main import (
    ConcurrentDBox,
    save as c_save,
    load as c_load,
)
from dbox.frozen.main import FrozenDBox, save as f_save, load as f_load
from dbox.mutable.main import DBox, save as m_save, load as m_load


def save(box: Union[DBox, FrozenDBox, ConcurrentDBox], filepath: str):
    """Save a DBox, FrozenDBox, or ConcurrentDBox to a file."""
    if type(box) is DBox:
        m_save(box, filepath)
    if type(box) is FrozenDBox:
        f_save(box, filepath)
    if type(box) is ConcurrentDBox:
        c_save(box, filepath)


def load(filepath: str) -> Union[DBox, FrozenDBox, ConcurrentDBox]:
    """Load a DBox, FrozenDBox, or ConcurrentDBox from a pickle file."""
    with open(filepath, "rb") as fh:
        saved = pickle.load(fh)
        if isinstance(saved, FrozenDBox):
            f_load(saved)  # mutates saved
            return saved
        elif "priority" in saved:
            return c_load(saved)
        else:
            return m_load(saved)
