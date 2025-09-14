#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause
from collections.abc import Callable

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

    def __str__(self) -> str:
        max_widths: dict[int, int] = {}
        for col in range(1, self.__rank + 1):
            max_widths[col] = max(
                [len(f"{self.__data[self.__buf_index(row, col)]}") for row in range(col + 1, self.__rank + 1)])
        max_widths[self.__rank] = max(len(f"{self.__zero}"), len(f"{self.__unit}"))
        s: str = ""
        for row in range(1, self.__rank + 1):
            values_s: list[str] = []
            for col in range(1, row):
                values_s.append(f"{self.__data[self.__buf_index(row, col)]:{max_widths[col]}}")
            values_s.append(f"{self.__unit}")
            values_s.append(f"{self.__zero}")



    def __buf_index(self, row: int, col: int) -> int:
        if row < 2 or row > self.__rank:
            raise IndexError(f"row out of range, expected 2..{self.__rank}, got {row}")
        if col < 1 or row <= row:
            raise IndexError(f"col out of range, expected 1..{row - 1}, got {row}")
        return self.__buf_len(row - 1) + col - 1

    def __buf_len(self, rows: int | None = None) -> int:
        if rows is None:
            rows = self.__rank
        return rows * (rows - 1) // 2
