#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause
import functools

import ievalg
from ievalg.f2 import m2_pow

Field = ievalg.UT.Field


def extract_common_factor(f: Field) -> tuple[Field, Field]:
    if f == Field.Unit or f == Field.Zero or len(f.value()) == 1:
        return Field.Unit, f

    factor_index: list[dict[str, int]] = [{sym: exp for sym, exp in m} for m in f.value()]

    common_symbols: set[str] = functools.reduce(lambda s, t: s & t, [set(d.keys()) for d in factor_index])

    common_symbol_min_exps: dict[str, int] = {sym: min({exp_map[sym] for exp_map in factor_index}) for sym in
                                              common_symbols}

    cf = ievalg.M2(sorted(ievalg.tot(*common_symbol_min_exps.items())))
    cf_inv = m2_pow(cf, -1)
    return Field(cf), f * cf_inv
