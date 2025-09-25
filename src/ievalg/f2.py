#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

from __future__ import annotations


def tot(*tuples: tuple[S2, int]) -> tuple[tuple[S2, int], ...]:
    return tuple((k, v) for k, v in tuples)


S2 = str

M2 = tuple[tuple[S2, int], ...]

F2 = set[M2]


def f2(initializer: F2 | M2) -> F2:
    if isinstance(initializer, set):
        return initializer.copy()
    return {initializer}


def m2_str(lhs: M2) -> str:
    if len(lhs) == 0:
        return "1"

    def factor_str(factor: tuple[S2, int]) -> str:
        sym, exp = factor
        if exp != 1:
            return f"{sym}^{exp}"
        return f"{sym}"

    return "*".join([factor_str(f) for f in lhs])


def m2_mul(lhs: M2, rhs: M2) -> M2:
    self_factors = {sym: exp for sym, exp in lhs}
    other_factors = {sym: exp for sym, exp in rhs}
    total_factors = self_factors.keys() | other_factors.keys()
    result_dict: dict[str, int] = {}
    for factor in total_factors:
        result_dict[factor] = self_factors.get(factor, 0) + other_factors.get(factor, 0)
    return M2(sorted([(k, v) for k, v in result_dict.items() if v != 0]))


def m2_pow(lhs: M2, p: int) -> M2:
    return M2((sym, exp * p) for sym, exp in lhs)


def m2_div(lhs: M2, rhs: M2) -> M2:
    return m2_mul(lhs, m2_pow(rhs, -1))


def f2_add(lhs: F2 | M2, rhs: F2 | M2) -> F2:
    return f2(lhs) ^ f2(rhs)


def f2_neg(lhs: F2 | M2) -> F2:
    return f2(lhs)


def f2_sub(lhs: F2 | M2, rhs: F2 | M2) -> F2:
    return f2_add(lhs, f2_neg(rhs))


def f2_mul(lhs: F2 | M2, rhs: F2 | M2) -> F2:
    acc: F2 = F2()
    for m in f2(rhs):
        sub_product: F2 = f2({m2_mul(lm, m) for lm in f2(lhs)})
        acc = f2_add(acc, sub_product)
    return acc


class Field2:
    __value: F2

    Zero: Field2
    Unit: Field2

    def __init__(self, init_val: Field2 | F2 | M2 | int | str):
        if isinstance(init_val, Field2):
            self.__value = f2(init_val.__value)
            return
        if isinstance(init_val, set):
            self.__value = f2(init_val)
            return
        if isinstance(init_val, int):
            if not init_val in [0, 1]:
                raise ValueError(f"invalid numeric field initializer: expected 0 or 1, got {init_val}")
            self.__value = F2()
            if init_val == 1:
                self.__value.add(M2())
            return
        if isinstance(init_val, str):
            self.__build_from_str(init_val)
            return
        m: M2 = M2(init_val)
        self.__value = F2()
        self.__value.add(m)

    def value(self) -> F2:
        return self.__value

    def __hash__(self) -> int:
        return hash(f"{self}")

    def __str__(self) -> str:
        if len(self.__value) == 0:
            return "0"
        return "+".join(sorted([m2_str(m) for m in self.__value]))

    def __format__(self, format_spec):
        return f"{str(self):{format_spec}}"

    def __eq__(self, other: Field2 | F2 | M2 | int | str) -> bool:
        return self.__value == Field2(other).__value

    def __add__(self, other: Field2 | F2 | M2 | int | str) -> Field2:
        return Field2(f2_add(self.__value, Field2(other).__value))

    def __sub__(self, other: Field2 | F2 | M2 | int | str) -> Field2:
        return Field2(f2_sub(self.__value, Field2(other).__value))

    def __mul__(self, other: Field2 | F2 | M2 | int | str) -> Field2:
        return Field2(f2_mul(self.__value, Field2(other).__value))

    def __neg__(self) -> Field2:
        return Field2(f2_neg(self.__value))

    def __build_from_str(self, value: str):
        self.__value = F2()
        for monomial_str in [ms.strip() for ms in value.split(sep="+")]:
            f_m: M2 | None = M2()
            for factor_str in [fs.strip() for fs in monomial_str.split(sep="*")]:
                if factor_str.isnumeric():
                    f_int = int(factor_str)
                    if f_int % 2 == 0:
                        f_m = None
                        break
                    if f_int % 2 == 1:
                        continue
                if "^" in factor_str:
                    symbol, exp = factor_str.split("^")
                    symbol = symbol.strip()
                    exp = int(exp.strip())
                else:
                    symbol, exp = factor_str.strip(), 1
                f_m = m2_mul(f_m, tot((symbol, exp)))
            if f_m is not None:
                self.__value = f2_add(self.__value, f_m)


Field2.Zero = Field2(0)
Field2.Unit = Field2(1)
