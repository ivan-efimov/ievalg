#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

from __future__ import annotations

from ievalg.characteristic import WithCharacteristic

ConvertibleToPrimeField = int | str


class PrimeField(WithCharacteristic):
    __value: int

    def value(self) -> int:
        return self.__value

    def __init__(self, value: ConvertibleToPrimeField = 0, char: int = 2, base: int = 10) -> None:
        super().__init__(char)
        if isinstance(value, str):
            value = int(value, base=base)
        self.__value = value % self.char()

    def __str__(self) -> str:
        return f"{self.value()}"

    def __format__(self, format_spec):
        return f"{str(self):{format_spec}}"

    def __eq__(self, other: PrimeField | ConvertibleToPrimeField) -> bool:
        return self.value() == self.__accept_operand(other).value()

    def __lt__(self, other: PrimeField | ConvertibleToPrimeField) -> bool:
        return self.value() < self.__accept_operand(other).value()

    def __gt__(self, other: PrimeField | ConvertibleToPrimeField) -> bool:
        return self.__accept_operand(other) < self

    def __le__(self, other: PrimeField | ConvertibleToPrimeField) -> bool:
        other = self.__accept_operand(other)
        return self < other or self == other

    def __ge__(self, other: PrimeField | ConvertibleToPrimeField) -> bool:
        other = self.__accept_operand(other)
        return self > other or self == other

    def __pow__(self, power: int, modulo: None = None) -> PrimeField:
        if power >= 0:
            return PrimeField(pow(self.value(), exp=power, mod=self.char()), char=self.char())
        elif power == -1:
            return self ** (self.char() - 2)
        else:
            return (self ** -1) ** -power

    def __neg__(self) -> PrimeField:
        return PrimeField(-self.value(), char=self.char())

    def __add__(self, other: PrimeField | ConvertibleToPrimeField) -> PrimeField:
        return PrimeField(self.value() + self.__accept_operand(other).value(), char=self.char())

    def __sub__(self, other: PrimeField | ConvertibleToPrimeField) -> PrimeField:
        return PrimeField(self.value() - self.__accept_operand(other).value(), char=self.char())

    def __mul__(self, other: PrimeField | ConvertibleToPrimeField) -> PrimeField:
        return PrimeField(self.value() * self.__accept_operand(other).value(), char=self.char())

    def __truediv__(self, other: PrimeField | ConvertibleToPrimeField) -> PrimeField:
        return self * (self.__accept_operand(other) ** -1)

    def __floordiv__(self, other: PrimeField | ConvertibleToPrimeField) -> PrimeField:
        return self / self.__accept_operand(other)

    def __hash__(self) -> int:
        return hash(self.value())

    def __accept_operand(self, op: PrimeField | ConvertibleToPrimeField) -> PrimeField:
        if isinstance(op, ConvertibleToPrimeField):
            op = PrimeField(op, char=self.char())
        else:
            self.compat(op)
        return op
