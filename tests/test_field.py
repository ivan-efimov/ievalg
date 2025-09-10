#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

from ievalg.field import Field


def test_basics():
    assert f"{Field('', char=2)}" == "0"
    assert Field('', char=2) == 0
    assert f"{Field(0, char=2)}" == "0"
    assert Field(0, char=2) == 0
    assert Field(1, char=2) == 1
    assert Field('c^3+a^2+b', char=2) == "a^2+b+c^3"
