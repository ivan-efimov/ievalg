#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

import itertools

import pytest

from ievalg.prime_field import PrimeField
from ievalg.small_prime import SmallPrimes

SmallValues = range(-17, 17 + 1)


@pytest.mark.parametrize("char", SmallPrimes)
@pytest.mark.parametrize("value", SmallValues)
def test_int_construction(char: int, value: int):
    elem = PrimeField(value=value, char=char)
    assert elem.value() == value % char


@pytest.mark.parametrize("char", SmallPrimes)
@pytest.mark.parametrize("value", [f"{i}" for i in SmallValues])
def test_decimal_str_construction(char: int, value: str):
    elem = PrimeField(value=value, char=char)
    assert elem.value() == int(value) % char


@pytest.mark.parametrize("char", SmallPrimes)
@pytest.mark.parametrize("value", [f"{i:X}" for i in SmallValues])
def test_hex_str_construction(char: int, value: str):
    elem = PrimeField(value=value, char=char, base=16)
    assert elem.value() == int(value, base=16) % char


@pytest.mark.parametrize("char", [53])
@pytest.mark.parametrize("value", SmallValues)
def test_print(char: int, value: int):
    elem = PrimeField(value=value, char=char)
    assert f"{elem.value()}" == f"{value % char}"


@pytest.mark.parametrize("char", [53])
@pytest.mark.parametrize("lhs", [v for v in SmallValues if abs(v) < 7])
@pytest.mark.parametrize("rhs", [v for v in SmallValues if abs(v) < 7])
def test_rel_op(char: int, lhs: int, rhs: int):
    pf_lhs = PrimeField(lhs, char=char)
    pf_rhs = PrimeField(rhs, char=char)

    m_lhs = lhs % char
    m_rhs = rhs % char

    if m_lhs == m_rhs:
        assert pf_lhs == pf_rhs
    if m_lhs != m_rhs:
        assert pf_lhs != pf_rhs
    if m_lhs <= m_rhs:
        assert pf_lhs <= pf_rhs
    if m_lhs >= m_rhs:
        assert pf_lhs >= pf_rhs
    if m_lhs < m_rhs:
        assert pf_lhs < pf_rhs
    if m_lhs > m_rhs:
        assert pf_lhs > pf_rhs


@pytest.mark.parametrize("char", SmallPrimes[::3])
@pytest.mark.parametrize("value", [v for v in SmallValues if 0 <= v])
@pytest.mark.parametrize("exp", [v for v in SmallValues if 0 <= v < 4])
def test_exp(char: int, value: int, exp: int):
    assert (PrimeField(value, char=char) ** exp) == pow(value, exp, mod=char)


@pytest.mark.parametrize("char", SmallPrimes)
@pytest.mark.parametrize("value", SmallValues)
def test_neg(char: int, value: int):
    assert -PrimeField(value, char=char) == PrimeField(-value, char=char)


@pytest.mark.parametrize("char", SmallPrimes)
def test_arithmetics(char: int):
    for i, j in itertools.product(range(char), range(char)):
        assert PrimeField(i, char=char) + PrimeField(j, char=char) == PrimeField(i + j, char=char)
        assert PrimeField(i, char=char) * PrimeField(j, char=char) == PrimeField(i * j, char=char)
        if PrimeField(i * j, char=char) == 1:
            assert PrimeField(i, char=char) ** -1 == PrimeField(j, char=char)
