#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

import ievalg


def f(val) -> ievalg.UT.Field:
    return ievalg.UT.Field(val)

def test_ut():
    rank = 4
    m1 = ievalg.UT(rank, lambda i, j: f(f"m{i}{j}"))

    ref = [
        [f(1), f(0), f(0), f(0)],
        [f("m21"), f(1), f(0), f(0)],
        [f("m31"), f("m32"), f(1), f(0)],
        [f("m41"), f("m42"), f("m43"), f(1)],
    ]

    for i in range(1, rank + 1):
        for j in range(1, rank + 1):
            assert m1[i, j] == ref[i - 1][j - 1]


def test_matmul():
    rank = 4
    a = ievalg.UT(rank, lambda i, j: f(f"a{i}{j}"))
    b = ievalg.UT(rank, lambda i, j: f(f"b{i}{j}"))

    ref = [
        [f(1), f(0), f(0), f(0)],
        [f("a21+b21"), f(1), f(0), f(0)],
        [f("a31+a32*b21+b31"), f("a32+b32"), f(1), f(0)],
        [f("a41+a42*b21+a43*b31+b41"), f("a42+a43*b32+b42"), f("a43+b43"), f(1)],
    ]

    ab = a @ b

    for i in range(1, rank + 1):
        for j in range(1, rank + 1):
            assert ab[i, j] == ref[i - 1][j - 1]
