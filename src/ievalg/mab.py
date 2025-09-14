#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause
import logging

import ievalg
from ievalg import Field


class MAB:
    char: int = 2

    __rank: int

    __constraints: dict[str, Field]
    __permissions_zero: set[str]
    __permissions_nonzero: set[str]

    __equations: set[Field]

    def __init__(self, rank: int, constraints: dict[str, Field], permissions_zero: set[str],
                 permissions_nonzero: set[str]):
        self.__rank = rank
        logging.info(f"Initializing MAB problem with rank = {self.__rank}")
        self.__constraints = constraints
        for l, r in self.__constraints.items():
            logging.info(f"Adding constraint: {l} = {r}")
        self.__permissions_zero = permissions_zero
        for p in self.__permissions_zero:
            logging.info(f"Adding permission: {p} == 0")
        self.__permissions_nonzero = permissions_nonzero
        for p in self.__permissions_nonzero:
            logging.info(f"Adding permission: {p} != 0")
        logging.info(f"PZ = {self.__permissions_zero}")
        logging.info(f"PNZ = {self.__permissions_nonzero}")

        self.__build_equations()

    def __build_equations(self):
        self.__equations = set()
        m = ievalg.UT(rank=self.__rank, initializer=self.__gen_m)
        a = ievalg.UT(rank=self.__rank, initializer=lambda i, j: self.__gen_ab("a", i, j))
        b = ievalg.UT(rank=self.__rank, initializer=lambda i, j: self.__gen_ab("b", i, j))
        aa = a @ a
        bb = b @ b
        ab = a @ b
        for row in range(2, self.__rank + 1):
            for col in range(1, row):
                logging.info(f"Adding equation AA[{row}, {col}] = 0 = {aa[row, col]}")
                self.__equations.add(aa[row, col])
                logging.info(f"Adding equation BB[{row}, {col}] = 0 = {bb[row, col]}")
                self.__equations.add(bb[row, col])
                logging.info(
                    f"Adding equation AB[{row}, {col}] - M[{row}, {col}] = {ab[row, col]} - {m[row, col]} = 0 = {ab[row, col] - m[row, col]}")
                self.__equations.add(ab[row, col] - m[row, col])

    def __gen_ab(self, sym: str, row: int, col: int) -> Field:
        if sym not in ["a", "b"]:
            raise ValueError(f"invalid sym: expected 'a'/'b', got {sym}")
        s = f"{sym}{row}{col}"
        val = self.__constraints.get(s, Field(s, char=self.char))
        if f"{val}" in self.__permissions_zero:
            return Field(0, char=self.char)
        return val

    def __gen_m(self, row: int, col: int) -> Field:
        val = Field(f"m{row}{col}", char=self.char)
        if f"{val}" in self.__permissions_zero:
            return Field(0, char=self.char)
        return val
