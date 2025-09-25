#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

from __future__ import annotations

from collections.abc import Callable, Iterable

import ievalg

Field_ = ievalg.Field2

UtGenerator = Callable[[int, int], Field_]

UtInitializer = UtGenerator | list[Field_]


class UT:
    __rank: int
    __data: list[Field_]
    __unit: Field_
    __zero: Field_

    Field = Field_

    unit: UT

    @staticmethod
    def abstract(rank: int, symbol: str) -> UT:
        return UT(rank, lambda i, j: UT.Field(f"{symbol}{i}{j}"))

    def __init__(self, rank: int, initializer: UtInitializer):
        self.__zero = Field_(0)
        self.__unit = Field_(1)
        if rank <= 1:
            raise ValueError("rank must be greater than 1")
        self.__rank = rank
        if isinstance(initializer, list):
            if len(initializer) != self.__buf_len():
                raise ValueError(
                    f"invalid initializer list length: expected {self.__buf_len()}, got {len(initializer)}")
            if not all([isinstance(x, Field_) for x in initializer]):
                raise TypeError(f"invalid initializer list element type: expected {Field_}, got {type(initializer)}")
            self.__data = initializer
        else:
            self.__data = [initializer(row, col) for row in range(2, self.__rank + 1) for col in range(1, row)]

    def rank(self) -> int:
        return self.__rank

    def __iter__(self) -> Iterable[tuple[int, int, Field_]]:
        return iter([(i, j, self[i, j]) for i in range(2, self.__rank + 1) for j in range(1, i)])

    def __str__(self) -> str:
        max_widths: dict[int, int] = {}
        for col in range(1, self.__rank + 1):
            max_widths[col] = 1
            for row in range(col + 1, self.__rank + 1):
                max_widths[col] = max([max_widths[col], len(f"{self[row, col]}")])
        s: str = "\n"
        for row in range(1, self.__rank + 1):
            s += ' '.join(
                [f'{self[row, col]:^{max_widths[col]}}' for col in range(1, row)] +
                [f'{self.__unit:^{max_widths[row]}}'] +
                [f'{self.__zero:^{max_widths[col]}}' for col in range(row + 1, self.__rank + 1)]
            ) + "\n"
        return s

    def __getitem__(self, row_col: tuple[int, int]) -> Field_:
        row = row_col[0]
        col = row_col[1]
        if row < 1 or row > self.__rank:
            raise IndexError(f"row out of range, expected 1..{self.__rank}, got {row}")
        if col < 1 or col > self.__rank:
            raise IndexError(f"col out of range, expected 1..{self.__rank}, got {col}")

        if col > row:
            return self.__zero
        if col == row:
            return self.__unit
        return self.__data[self.__buf_index(row, col)]

    def __setitem__(self, row_col: tuple[int, int], value: Field_):
        row = row_col[0]
        col = row_col[1]
        if row < 1 or row > self.__rank:
            raise IndexError(f"row out of range, expected 1..{self.__rank}, got {row}")
        if col < 1 or col >= row:
            raise IndexError(f"col out of range, expected 1..{row - 1}, got {col}")

        self.__data[self.__buf_index(row, col)] = value

    def __matmul__(self, other: UT) -> UT:
        result = UT(self.__rank, [ievalg.Field2.Zero] * self.__buf_len())
        for row in range(2, self.__rank + 1):
            for col in range(1, row):
                val = self[row, col] + other[row, col]
                for k in range(col + 1, row):
                    val = val + self[row, k] * other[k, col]
                result[row, col] = val
        return result

    def __sub__(self, other: UT) -> UT:
        result = UT(self.__rank, [ievalg.Field2.Zero] * self.__buf_len())
        for i in range(self.__buf_len()):
            result.__data[i] = self.__data[i] + other.__data[i]
        return result

    def __buf_index(self, row: int, col: int) -> int:
        if row < 2 or row > self.__rank:
            raise IndexError(f"row out of range, expected 2..{self.__rank}, got {row}")
        if col < 1 or col >= row:
            raise IndexError(f"col out of range, expected 1..{row - 1}, got {col}")
        return self.__buf_len(row - 1) + col - 1

    def __buf_len(self, rows: int | None = None) -> int:
        if rows is None:
            rows = self.__rank
        return rows * (rows - 1) // 2
