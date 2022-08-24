import pickle
from typing import Union

from filterbox.concurrent.main import (
    ConcurrentFilterBox,
    save as c_save,
    load as c_load,
)
from filterbox.frozen.main import FrozenFilterBox, save as f_save, load as f_load
from filterbox.mutable.main import FilterBox, save as m_save, load as m_load


def save(box: Union[FilterBox, FrozenFilterBox, ConcurrentFilterBox], filepath: str):
    """Save a FilterBox, FrozenFilterBox, or ConcurrentFilterBox to a file."""
    if type(box) is FilterBox:
        m_save(box, filepath)
    if type(box) is FrozenFilterBox:
        f_save(box, filepath)
    if type(box) is ConcurrentFilterBox:
        c_save(box, filepath)


def load(filepath: str) -> Union[FilterBox, FrozenFilterBox, ConcurrentFilterBox]:
    """Load a FilterBox, FrozenFilterBox, or ConcurrentFilterBox from a pickle file."""
    with open(filepath, "rb") as fh:
        saved = pickle.load(fh)
        if isinstance(saved, FrozenFilterBox):
            f_load(saved)  # mutates saved
            return saved
        elif "priority" in saved:
            return c_load(saved)
        else:
            return m_load(saved)
