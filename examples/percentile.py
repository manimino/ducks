"""
Look up objects by the percentile rank of an attribute.
In this example, we find requests with latency > p99 (99th percentile)
and requests with median latency (50th percentile).
"""

import functools
from bisect import bisect_left
import numpy as np
from typing import Any

from filtered import Filtered


def percentile(cutoffs: np.ndarray, attr: str, obj: Any) -> int:
    """Compute percentile on obj[attr] according to the cutoffs."""
    p = bisect_left(cutoffs, obj[attr])
    # handle values that are outside the min and max of cutoffs.
    # can happen due to float precision errors, or when new data is added.
    if p < 0:
        return 0
    if p > 99:
        return 99
    return p


def main():
    objs = [{"num": i, "latency": 1 + (i / 100) ** 3} for i in range(1000)]
    # make an array of size 100 containing the min cutoff values for each percentile
    latencies = np.array([obj["latency"] for obj in objs])
    cutoffs = np.quantile(latencies, np.linspace(0, 1, 100))
    p_latency = functools.partial(percentile, cutoffs, "latency")
    f = Filtered(objs, [p_latency])
    print("requests with first-percentile latency:")
    for obj in f.find({p_latency: [0, 1]}):
        print(obj)
    print("\nrequests with median (50th percentile) latency:")
    for obj in f.find({p_latency: 50}):
        print(obj)
    print("\nrequests with 99th percentile latency:")
    for obj in f.find({p_latency: 99}):
        print(obj)


if __name__ == "__main__":
    main()
