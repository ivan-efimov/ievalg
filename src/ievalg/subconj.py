#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause
from copy import deepcopy

import ievalg
from ievalg import UT


def subconj(m: UT) -> UT:
    subsets: list[set[int]] = []

    sc = deepcopy(m)

    zero = ievalg.Field(0, char=m.char())

    in_subset: bool = False
    for i in range(2, m.rank() + 1):
        if sc[i, i - 1] != zero:
            if not in_subset:
                subsets.append(set())
                in_subset = True
            subsets[-1].add(i)
        elif in_subset:
            in_subset = False

    maximals: set[int] = set()
    union_set: set[int] = set()

    for ss in subsets:
        maximals.add(max(ss))
        union_set = union_set | ss

    subdiag_n: int = 1
    for i in range(2 + subdiag_n, m.rank() + 1):
        for j in range(1, i - subdiag_n):
            if j + 1 in union_set or (i in union_set and j not in maximals):
                sc[i, j] = zero

    return sc
