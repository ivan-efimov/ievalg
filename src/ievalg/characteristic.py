#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

from __future__ import annotations

from ievalg.small_prime import is_small_prime


class WithCharacteristic:
    __char: int

    def __init__(self, char: int):
        if not is_small_prime(char):
            raise ValueError(f"invalid characteristic: expected prime < 100, got {char}")
        self.__char = char

    def compat(self, other: WithCharacteristic):
        if self.__char != other.__char:
            raise RuntimeError(f"incompatible characteristics: {self.__char} != {other.__char}")

    def char(self) -> int:
        return self.__char
