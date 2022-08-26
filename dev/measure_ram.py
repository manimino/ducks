"""
This script was used to measure RAM usage of different collection sizes.
This was used during design; it's not relevant to users of Dex.
"""

import os
import subprocess
import sys

import numpy as np

from array import array
from cykhash import Int64Set


TOT_ITEMS = 10 ** 6

print_names = {
    "pytup": "tuple",
    "pyset": "set",
    "pyarr": "array (int64)",
    "cyk": "cykhash Int64Set",
    "nparr": "numpy array (int64)",
    "btree": "BTrees.LLBTree",
}


def get_ram():
    return (
        int(
            os.popen(f"ps -o pid,rss -p {os.getpid()}").read().split("\n")[1].split()[1]
        )
        * 1024
    )


def cyk(items_per=10):
    n_sets = TOT_ITEMS // items_per
    ls = [None for _ in range(n_sets)]
    baseline = get_ram()
    for i in range(n_sets):
        offset = i * items_per
        iset = Int64Set(range(offset, offset + items_per))
        ls[i] = iset
    used = get_ram() - baseline
    ram = round(used / TOT_ITEMS, 1)
    print("cykhash_set", items_per, ram)


def nparr(items_per=10):
    n_sets = TOT_ITEMS // items_per
    ls = [None for _ in range(n_sets)]
    baseline = get_ram()
    for i in range(n_sets):
        offset = i * items_per
        ls[i] = np.array(range(offset, offset + items_per))
    used = get_ram() - baseline
    ram = round(used / TOT_ITEMS, 1)
    print("Numpy_array", items_per, ram)


def pyset(items_per=10):
    n_sets = TOT_ITEMS // items_per
    ls = [None for _ in range(n_sets)]
    baseline = get_ram()
    for i in range(n_sets):
        offset = i * items_per
        iset = set(range(offset, offset + items_per))
        ls[i] = iset
    used = get_ram() - baseline
    ram = round(used / TOT_ITEMS, 1)
    print("python_set", items_per, ram)


def pytup(items_per=10):
    n_tups = TOT_ITEMS // items_per
    baseline = get_ram()
    ls = [None for _ in range(n_tups)]
    for i in range(n_tups):
        offset = i * items_per
        ls[i] = tuple(range(offset, offset + items_per))
    used = get_ram() - baseline
    ram = round(used / TOT_ITEMS, 1)
    print("python_tuple", items_per, ram)


def pyarr(items_per=10):
    n_arrs = TOT_ITEMS // items_per
    baseline = get_ram()
    ls = [None for _ in range(n_arrs)]
    for i in range(n_arrs):
        arr = array("q")
        offset = i * items_per
        arr.extend(range(offset, offset + items_per))
        ls[i] = arr
    used = get_ram() - baseline
    ram = round(used / TOT_ITEMS, 1)
    print("python_array", items_per, ram)


def main(method, items_per):
    iper = int(items_per)
    if method == "pytup":
        f = pytup
    elif method == "pyset":
        f = pyset
    elif method == "cyk":
        f = cyk
    elif method == "nparr":
        f = nparr
    elif method == "pyarr":
        f = pyarr
    else:
        print("what?!", method)
        raise ValueError()
    f(iper)


def row_dict_to_table(rd):
    # makes a github markdown table out of a dict of {row: {column: value}}
    # kinda jank looking but pycharm's autoformatter will fix it
    for r in rd:
        header = "|   |" + " | ".join(str(x) for x in rd[r])
        print()
        break
    print(header + "   |")
    dashes = ["|---"]
    for r in rd:
        for k in rd[r]:
            dashes.append("-" * (2 + len(str(rd[r][k]))))
        break
    print("|".join(dashes) + "---|")
    for r in rd:
        s = "| " + print_names[r] + " | "
        s += " | ".join(str(x) for x in rd[r].values())
        print(s + "   |")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1], sys.argv[2])
    else:
        results = dict()
        for method in ["pyset", "pytup", "pyarr", "cyk", "nparr"]:
            m_result = dict()
            for items_per in [1, 2, 3, 4, 5, 10, 25, 50, 100, 1000, 10000]:
                txt = subprocess.check_output(
                    f"python measure_ram.py {method} {items_per}".split()
                )
                res = txt.decode().strip()
                _, _, bytes_per = res.split()
                m_result[items_per] = bytes_per
            results[method] = m_result
        print(results)
        row_dict_to_table(results)
