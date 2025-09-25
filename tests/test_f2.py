#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

import pytest

import ievalg

cases = [
    ("0", "0", "0", "0"),
    ("0", "1", "1", "0"),
    ("1", "0", "1", "0"),
    ("1", "1", "0", "1"),
    ("0", "a", "a", "0"),
    ("a", "0", "a", "0"),
    ("1", "a", "1+a", "a"),
    ("a", "1", "1+a", "a"),
    ("a", "a", "0", "a^2"),
    ("a", "b", "a+b", "a*b"),
    ("a+b", "b+c", "a+c", "a*b+a*c+b*c+b^2"),
    ("a", "a^-1", "a^-1+a", "1"),
    ("a^2", "a^-2", "a^-2+a^2", "1"),
    ("a+b", "a+b", "0", "a^2+b^2"),
    ("a+b+c", "a+b+c", "0", "a^2+b^2+c^2"),
    ("a*b^2+c", "a+a*b*c+b^-3", "a+a*b*c+a*b^2+b^-3+c", "a*b*c^2+a*b^-1+a*c+a^2*b^2+a^2*b^3*c+c*b^-3"),
]


@pytest.mark.parametrize("fld1,fld2,summ,product", cases)
def test_f2(fld1, fld2, summ, product):
    _1 = ievalg.Field2(fld1)
    _2 = ievalg.Field2(fld2)
    _1_2 = ievalg.Field2(summ)
    _12 = ievalg.Field2(product)

    assert _1 + _2 == _1_2
    assert _1 * _2 == _12
