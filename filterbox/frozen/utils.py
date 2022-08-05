import numpy as np
import sortednp as snp


def snp_difference(left: np.ndarray, right: np.ndarray):
    # difference = left - indices_in_intersection(left, right)
    _, indices = snp.intersect(left, right, indices=True)
    indices_to_discard = indices[0]
    keep_these = np.ones_like(left, dtype=bool)
    keep_these[indices_to_discard] = False
    return left[keep_these]
