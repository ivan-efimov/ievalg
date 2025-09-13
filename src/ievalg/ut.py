#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause
from collections.abc import Callable

from ievalg import Field

UtGenerator = Callable[[int, int], Field]

UtInitializer = UtGenerator | list[list[Field]] | list[Field]


class UT:
    __rank: int
    __data: list[Field]

    def __init__(self, init: UtInitializer | None = None):
        __data: list[Field] = [Field(0)]
        if isinstance(init, list):
            pass
