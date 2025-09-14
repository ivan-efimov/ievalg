#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

import ievalg


def test_ut():
    rank = 4
    m1 = ievalg.UT(rank, lambda i, j: ievalg.Field(f"m{i}{j}"))

    def f(val) -> ievalg.Field:
        return ievalg.Field(val)

    ref = [
        [ievalg.Field(1), ievalg.Field(0), ievalg.Field(0), ievalg.Field(0)],
        [ievalg.Field("m21"), ievalg.Field(1), ievalg.Field(0), ievalg.Field(0)],
        [ievalg.Field("m31"), ievalg.Field("m32"), ievalg.Field(1), ievalg.Field(0)],
        [ievalg.Field("m41"), ievalg.Field("m42"), ievalg.Field("m43"), ievalg.Field(1)],
    ]

    for i in range(1, rank + 1):
        for j in range(1, rank + 1):
            assert m1[i, j] == ref[i - 1][j - 1]


def test_matmul():
    rank = 4
    a = ievalg.UT(rank, lambda i, j: ievalg.Field(f"a{i}{j}"))
    b = ievalg.UT(rank, lambda i, j: ievalg.Field(f"b{i}{j}"))

    def f(val) -> ievalg.Field:
        return ievalg.Field(val)

    ref = [
        [ievalg.Field(1), ievalg.Field(0), ievalg.Field(0), ievalg.Field(0)],
        [ievalg.Field("a21+b21"), ievalg.Field(1), ievalg.Field(0), ievalg.Field(0)],
        [ievalg.Field("a31+a32*b21+b31"), ievalg.Field("a32+b32"), ievalg.Field(1), ievalg.Field(0)],
        [ievalg.Field("a41+a42*b21+a43*b31+b41"), ievalg.Field("a42+a43*b32+b42"), ievalg.Field("a43+b43"),
         ievalg.Field(1)],
    ]

    ab = a @ b

    for i in range(1, rank + 1):
        for j in range(1, rank + 1):
            assert ab[i, j] == ref[i - 1][j - 1]
