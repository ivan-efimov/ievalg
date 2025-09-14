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
