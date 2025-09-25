#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

import pytest

import ievalg


@pytest.mark.parametrize("f,cf,bf", [
    ("0", "1", "0"),
    ("1+a^2", "1", "1+a^2"),
    ("a^2+b^2", "1", "a^2+b^2"),
    ("a^2+a*b^2", "a", "a+b^2"),
    ("a^2*c^-5+a*b^2*c^3", "a*c^-5", "a+b^2*c^8"),
])
def test_extract_common_factor(f: str, cf: str, bf: str):
    cf_f, bf_f = ievalg.extract_common_factor(ievalg.Field2(f))
    assert f"{cf_f}" == cf
    assert f"{bf_f}" == bf
