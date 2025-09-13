#!/usr/bin/env python3

#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("rank", type=int,
                        help="Rank of the matrix")
    args = parser.parse_args()

    # rank-1 subdiagonal elements
    n = args.rank - 1

    elems: set[str] = set()

    for i in range(2 ** n):
        elem = f"{i:0{n}b}"
        if not elem[::-1] in elems:
            elems.add(elem)

    def n_zeroes(s: str):
        return s.count("0") * (2 ** n) + int(s, base=2)

    # print(f"|elems| = {len(elems)}")
    last_elem_size = None
    counter = 1
    for elem in sorted(list(elems), key=n_zeroes):
        elem_size = elem.count("0")
        if not last_elem_size or last_elem_size != elem_size:
            last_elem_size = elem_size
            # print(f"===  {elem_size:3d}  ===")
        inits = [
            # "$0$" if elem[i] == "0" else f"$m_({i+2}{i+1})$"
            '"0"_F' if elem[i] == "0" else f'"m{i + 2}{i + 1}"_F'
            for i in range(len(elem))
        ]
        # print(f"    [{counter}],  {', '.join(inits)},")
        print(f"{{{', '.join(inits)}}},")
        counter += 1


if __name__ == "__main__":
    main()
