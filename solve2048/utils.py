from typing import List


def justify_table(table: List[List[str]]) -> str:
    maxlens = []

    for row in table:
        for i, col in enumerate(row):
            len_ = len(col)
            try:
                maxlens[i] = max(maxlens[i], len_)
            except IndexError:
                maxlens.append(len_)

    rv = ""
    for row in table:
        for i, col in enumerate(row):
            rv += col.ljust(maxlens[i], " ") + "\t"
        rv += "\n"
    return rv
