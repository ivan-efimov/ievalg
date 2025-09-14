#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

from __future__ import annotations

from collections.abc import Callable, Iterable

from ievalg import Field

UtGenerator = Callable[[int, int], Field]

UtInitializer = UtGenerator | list[Field]


class UT:
    __rank: int
    __data: list[Field]
    __unit: Field
    __zero: Field

    def __init__(self, rank: int, initializer: UtInitializer):
        if rank <= 1:
            raise ValueError("rank must be greater than 1")
        self.__rank = rank
        char: int | None = None
        if isinstance(initializer, list):
            if len(initializer) != self.__buf_len():
                raise ValueError(
                    f"invalid initializer list length: expected {self.__buf_len()}, got {len(initializer)}")
            char = initializer[0].char()
            if not all([isinstance(x, Field) for x in initializer]):
                raise TypeError(f"invalid initializer list element type: expected {Field}, got {type(initializer)}")
            if not all([x.char() == char for x in initializer]):
                raise ValueError(f"inconsistent characteristics in initializer generator")
            self.__data = initializer
        else:
            self.__data = []
            for row in range(2, self.__rank + 1):
                for col in range(1, row):
                    new_element = initializer(row, col)
                    if char is None:
                        char = new_element.char()
                    elif char != new_element.char():
                        raise ValueError(f"inconsistent characteristics in initializer generator")
                    self.__data.append(new_element)
        self.__zero = Field(0, char=char)
        self.__unit = Field(1, char=char)

    def rank(self) -> int:
        return self.__rank

    def char(self) -> int:
        return self.__data[0].char()

    def __iter__(self) -> Iterable[tuple[int, int, Field]]:
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

    def __getitem__(self, row_col: tuple[int, int]) -> Field:
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

    def __setitem__(self, row_col: tuple[int, int], value: Field):
        row = row_col[0]
        col = row_col[1]
        if row < 1 or row > self.__rank:
            raise IndexError(f"row out of range, expected 1..{self.__rank}, got {row}")
        if col < 1 or col >= row:
            raise IndexError(f"col out of range, expected 1..{row - 1}, got {col}")

        self.__data[self.__buf_index(row, col)] = value

    def __matmul__(self, other: UT) -> UT:
        char = self.__data[0].char()
        result = UT(self.__rank, [Field(0, char=char)] * self.__buf_len())
        for row in range(2, self.__rank + 1):
            for col in range(1, row):
                # c51 = a51 + a52*b21 + a53*b31 + a54*b41 + b51
                val = self[row, col] + other[row, col]
                for k in range(col + 1, row):
                    val = val + self[row, k] * other[k, col]
                result[row, col] = val
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
