import numpy as np
import sortednp as snp


def snp_difference(left: np.ndarray, right: np.ndarray):
    # difference = left - indexes_in_intersection(left, right)
    _, indexes = snp.intersect(left, right, indices=True)
    indexes_to_discard = indexes[0]
    keep_these = np.ones_like(left, dtype=bool)
    keep_these[indexes_to_discard] = False
    return left[keep_these]
