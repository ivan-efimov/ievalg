#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

from __future__ import annotations

from ievalg.characteristic import WithCharacteristic
from ievalg.prime_field import PrimeField


class HDict(dict):
    def __hash__(self):
        return hash(f"{sorted(self.items())}")


Exp = int
Factors = HDict[str, Exp]

ConvertibleToField = str | PrimeField | int

FieldMembers = dict[Factors, PrimeField]


class Field(WithCharacteristic):
    __members: FieldMembers

    def __init__(self, value: ConvertibleToField, char: int = 2):
        super().__init__(char)
        self.__members = {}
        if isinstance(value, PrimeField | int):
            if isinstance(value, int):
                value = PrimeField(value, char=self.char())
            self.__members[HDict({})] = value
        else:
            self.__build_from_str(value)
        self.__remove_trivial_members()

    def members(self) -> FieldMembers:
        return self.__members

    def __str__(self) -> str:
        if len(self.members()) == 0:
            return "0"
        members = [(Field.__factors_to_str(k), v) for k, v in self.members().items()]
        members.sort(key=lambda x: x[0])
        # for members
        return "+".join([f"{Field.__coef_to_str(coef, len(factors) == 0)}{factors}" for factors, coef in members])

    def __format__(self, format_spec):
        return f"{str(self):{format_spec}}"

    def __eq__(self, other: Field | ConvertibleToField) -> bool:
        return self.members() == self.__accept_operand(other).members()

    def __pow__(self, power: int, modulo: None = None) -> Field:
        if power == 0:
            return Field(1, char=self.char())
        if power < 0 and len(self.members()) > 1:
            raise ValueError("negative powers are currently not supported for multi-member Field")
        new_f: Field = Field(0, char=self.char())
        for factors, coef in self.members():
            new_factors = HDict({})
            for f in factors.keys():
                new_factors[f] = factors[f] * power
            new_f.__members[new_factors] = coef ** power
        return new_f

    def __neg__(self) -> Field:
        new_f: Field = Field(0, char=self.char())
        for factors, coef in self.members():
            new_f.__members[factors] = -coef
        return new_f

    def __add__(self, other: Field | ConvertibleToField) -> Field:
        new_f: Field = Field(0, char=self.char())
        new_f.__members = self.__members.copy()
        for factors, coef in self.__accept_operand(other).members().items():
            new_f.__members[factors] = self.__members.get(factors, PrimeField(0, char=self.char())) + coef
        new_f.__remove_trivial_members()
        return new_f

    def __sub__(self, other: Field | ConvertibleToField) -> Field:
        return self + (-other)

    def __mul__(self, other: Field | ConvertibleToField) -> Field:
        new_f: Field = Field(0, char=self.char())
        new_f.__members = {}
        for factors, coef in self.__accept_operand(other).members().items():
            for self_factors, self_coef in self.members().items():
                new_factors = HDict(
                    {key: factors.get(key, 0) + self_factors.get(key, 0) for key in (factors | self_factors)})
                new_f.__members[new_factors] = new_f.__members.get(new_factors,
                                                                   PrimeField(0, char=self.char())) + coef * self_coef
        new_f.__remove_trivial_members()
        return new_f

    def __accept_operand(self, op: Field | ConvertibleToField) -> Field:
        if isinstance(op, ConvertibleToField):
            op = Field(op, char=self.char())
        else:
            self.compat(op)
        return op

    def __build_from_str(self, value: str):
        for monomial_str in [v.strip() for v in value.split(sep="+")]:
            factors, coef = self.__parse_monomial(monomial_str)
            if coef == 0:
                continue
            self.members()[factors] = self.members().get(factors, PrimeField(0, char=self.char())) + coef

    def __parse_monomial(self, value: str) -> tuple[Factors, PrimeField]:
        if value == "":
            return HDict({}), PrimeField(0, char=self.char())

        factors: Factors = HDict({})
        coef: PrimeField = PrimeField(1, char=self.char())

        for factor_str in [v.strip() for v in value.split(sep="*")]:
            if "^" in factor_str:
                symbol, exp = factor_str.split("^")
                symbol = symbol.strip()
                exp = int(exp.strip())
            else:
                symbol, exp = factor_str.strip(), 1
            if symbol.isnumeric():
                coef = coef * PrimeField(int(symbol), char=self.char())
            elif exp != 0:
                factors[symbol] = factors.get(symbol, 0) + exp

        return factors, coef

    def __remove_trivial_members(self):
        for key in list(self.members().keys()):
            if self.members()[key] == 0:
                self.__members.pop(key)

    @staticmethod
    def __factors_to_str(factors: Factors) -> str:
        return "*".join([f"{x}{Field.__exp_to_str(factors[x])}" for x in sorted(factors.keys())])

    @staticmethod
    def __exp_to_str(exp: int) -> str:
        if exp != 1:
            return f"^{exp}"
        return ""

    @staticmethod
    def __coef_to_str(coef: PrimeField, trivial_factors: bool) -> str:
        if trivial_factors:
            return f"{coef}"
        if coef != 1:
            return f"{coef}*"
        return ""
