import os
import psutil
import subprocess
import sys

from cykhash import Int64Set
import numpy as np


TOT_ITEMS = 5 * 10 ** 7


def cyk(items_per=10):
    n_sets = TOT_ITEMS // items_per
    ls = []
    process = psutil.Process(os.getpid())
    baseline = process.memory_info().rss
    for i in range(n_sets):
        iset = Int64Set()
        for j in range(items_per):
            iset.add(j)
        ls.append(iset)
    used = process.memory_info().rss - baseline
    ram = round(used / TOT_ITEMS, 1)
    print("cykhash_set", items_per, ram)


def nparr(items_per=10):
    n_sets = TOT_ITEMS // items_per
    ls = []
    process = psutil.Process(os.getpid())
    baseline = process.memory_info().rss
    for i in range(n_sets):
        ls.append(np.array(range(items_per)))
    used = process.memory_info().rss - baseline
    ram = round(used / TOT_ITEMS, 1)
    print("Numpy_array", items_per, ram)


def pyset(items_per=10):
    n_sets = TOT_ITEMS // items_per
    ls = []
    process = psutil.Process(os.getpid())
    baseline = process.memory_info().rss
    for i in range(n_sets):
        iset = set()
        for j in range(items_per):
            iset.add(j)
        ls.append(iset)
    used = process.memory_info().rss - baseline
    ram = round(used / TOT_ITEMS, 1)
    print("python_set", items_per, ram)


def pytup(items_per=10):
    n_tups = TOT_ITEMS // items_per
    ls = []
    process = psutil.Process(os.getpid())
    baseline = process.memory_info().rss
    for i in range(n_tups):
        ls.append(tuple(range(items_per)))
    used = process.memory_info().rss - baseline
    ram = round(used / TOT_ITEMS, 1)
    print("python_tuple", items_per, ram)


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
        s = "| " + r + " | "
        s += " | ".join(str(x) for x in rd[r].values())
        print(s + "   |")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1], sys.argv[2])
    else:
        results = dict()
        for method in ["pytup", "pyset", "cyk", "nparr"]:
            m_result = dict()
            for items_per in [1, 10, 50, 100, 1000, 10000]:
                txt = subprocess.check_output(
                    f"python measure_ram.py {method} {items_per}".split()
                )
                res = txt.decode().strip()
                _, _, bytes_per = res.split()
                m_result[items_per] = bytes_per
            results[method] = m_result
        print(results)
        row_dict_to_table(results)
