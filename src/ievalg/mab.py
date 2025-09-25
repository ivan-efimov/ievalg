#  Copyright (c) 2025. Ivan Efimov <va1319@yandex.ru>
#  BSD-3-Clause
import enum
import functools
import itertools
import logging

logger = logging.getLogger(__name__)

import ievalg

Field = ievalg.UT.Field

Constraints = dict[str, Field]
PermissionsZ = set[str]
PermissionsNZ = set[str]


class SymbolClass(enum.Enum):
    VARIABLE = 0
    CONSTANT = 1
    NONZERO_CONSTANT = 2


def gen_mab_problem(rank: int, m_mask: tuple[int, ...]) -> tuple[PermissionsZ, PermissionsNZ]:
    log = logger.getChild(gen_mab_problem.__name__)
    if len(m_mask) != rank - 1 or not all([x in (0, 1) for x in m_mask]):
        raise ValueError(f"invalid m_mask: expected {['0|1'] * (rank - 1)}, got {m_mask}")
    log.info(f"Generating MAB initial problem inputs for rank = {rank}, M-mask = {m_mask}")
    m = ievalg.UT.abstract(rank, "m")
    for i, k in enumerate(m_mask):
        m[i + 2, i + 1] = Field(k)
    l = ievalg.subconj(m)
    log.debug(f"M = {m}")
    log.debug(f"L = subconj(M) = {l}")

    permissions_zero: PermissionsZ = PermissionsZ()
    permissions_nonzero: PermissionsNZ = PermissionsNZ()

    for i, j, val in l:
        if val == 0:
            permissions_zero.add(f"m{i}{j}")
        elif i == j + 1:
            permissions_nonzero.add(f"m{i}{j}")

    log.debug(f"Permissions ZERO: {sorted(permissions_zero)}")
    log.debug(f"Permissions NON-ZERO: {sorted(permissions_nonzero)}")

    return permissions_zero, permissions_nonzero


class MabContradiction(RuntimeError):
    def __init__(self, what: str = "unspecified contradiction"):
        super().__init__(f"Contradiction: {what}")


class MabCouldntSolve(RuntimeError):
    def __init__(self, what: str = "unspecified reason"):
        super().__init__(f"Couldn't Solve: {what}")


def set_iu(iu: tuple[set[str], set[str]], s: set[str]) -> tuple[set[str], set[str]]:
    return iu[0] & s, iu[1] | s


def resolve_eq(eq: Field, sym_classifier) -> tuple[str, Field] | None:
    factor_index: list[dict[str, int]] = [{sym: exp for sym, exp in m} for m in sorted(eq.value())]

    _, all_symbols = functools.reduce(set_iu, [set(d.keys()) for d in factor_index], (set(), set()))
    all_vars: set[str] = {sym for sym in all_symbols if sym_classifier(sym) == SymbolClass.VARIABLE}
    if len(all_vars) == 0:
        raise MabContradiction(f"{eq} != {0}")
    if len(all_vars) > 1:
        return None
    var = list(all_vars)[0]
    exps = [fi.get(var, 0) for fi in factor_index]
    if all([exp in [0, 1] for exp in exps]) and exps.count(1) == 1:
        v_member_index = exps.index(1)
        v_member = sorted(eq.value())[v_member_index]
        rhs = eq - v_member
        v_member_inv = tuple((sym, -exp) for sym, exp in v_member if sym != var)
        return var, rhs * v_member_inv
    return None


def check_zero_group(eq: Field, sym_classifier) -> list[str] | None:
    if len(eq.value()) != 1:
        return None
    vs = [sym for sym, _ in list(eq.value())[0] if sym_classifier(sym) == SymbolClass.VARIABLE]
    if len(vs) > 1:
        return sorted(vs)
    return None


def check_nonzero_sum_group(eq: Field, sym_classifier) -> list[str] | None:
    if len(eq.value()) < 1:
        return None
    vs = [sym for sym, _ in list(eq.value())[0] if sym_classifier(sym) == SymbolClass.VARIABLE]
    if len(vs) > 1:
        return sorted(vs)
    return None


def check_linear(eq: Field, sym_classifier) -> tuple[str, Field, list[Field]] | None:
    if len(eq.value()) <= 1:
        return None

    factor_index: list[dict[str, int]] = [{sym: exp for sym, exp in m} for m in sorted(eq.value())]

    free_members = [m for m in factor_index if all([sym_classifier(sym) != SymbolClass.VARIABLE for sym in m.keys()])]
    free_members = [Field(ievalg.tot(*sorted(kv for kv in fm.items()))) for fm in free_members]

    for fi in factor_index:
        local_vars = [sym for sym in fi.keys() if sym_classifier(sym) == SymbolClass.VARIABLE]
        if len(local_vars) != 1 or fi[local_vars[0]] != 1:
            continue
        v = local_vars[0]
        return v, Field(ievalg.tot(*sorted(kv for kv in fi.items() if kv[0] != v))), free_members
    return None


def mab_solve(rank: int, constraints: Constraints, permissions_zero: PermissionsZ,
              permissions_nonzero: PermissionsNZ, lastz_a: bool = True, free_const_idx: int = 0,
              progress_bar: str = "") -> tuple[ievalg.UT, ievalg.UT] | None:
    log = logger.getChild(mab_solve.__name__)

    log.info(f"Solving MAB for rank = {rank}")
    log.warning(progress_bar)

    for l, r in constraints.items():
        log.debug(f"With constraint: {l} = {r}")
    log.debug(f"With permissions `== 0`: {permissions_zero}")
    log.debug(f"With permissions `!= 0`: {permissions_nonzero}")

    def sym_classifier(sym: str) -> SymbolClass:
        if sym.startswith("a") or sym.startswith("b"):
            return SymbolClass.VARIABLE
        if sym in permissions_nonzero:
            return SymbolClass.NONZERO_CONSTANT
        return SymbolClass.CONSTANT

    def gen_m(row: int, col: int) -> Field:
        val = Field(f"m{row}{col}")
        if f"{val}" in permissions_zero:
            return Field.Zero
        return val

    def gen_ab(sym: str, row: int, col: int) -> Field:
        if sym not in ["a", "b"]:
            raise ValueError(f"invalid sym: expected 'a'/'b', got {sym}")
        s = f"{sym}{row}{col}"
        val = constraints.get(s, Field(s))
        if f"{val}" in permissions_zero:
            return Field.Zero
        return val

    m = ievalg.UT(rank=rank, initializer=gen_m)
    a = ievalg.UT(rank=rank, initializer=lambda i, j: gen_ab("a", i, j))
    b = ievalg.UT(rank=rank, initializer=lambda i, j: gen_ab("b", i, j))
    aa = a @ a
    bb = b @ b
    ab = a @ b
    abm = ab - m

    morder = [bb, aa, abm] if lastz_a else [aa, bb, abm]

    log.info(f"A@A = {aa}")
    log.info(f"B@B = {aa}")
    log.info(f"A@B-M = {ab - m}")

    # equations_unsorted = {}
    equations = []
    # for col in range(1, rank):
    #     for row in range(col+1, rank + 1):
    for row in range(2, rank + 1):
        for col in range(1, row):
            for matrix in morder:
                if matrix[row, col] != 0:
                    cf, eq = ievalg.extract_common_factor(matrix[row, col])
                    equations.append(eq)

    # equations = []
    # for i in range(2, rank + 1):
    #     for j in range(i, rank+1):
    #         row, col = (j, 1+j-i)
    #         for s in ["a", "b", "m"]:
    #             if (row, col, s) in equations_unsorted:
    #                 equations.append(equations_unsorted[(row, col, s)])

    if len(equations) == 0:
        log.warning(f"Solved!")
        with open("result.txt", "a") as f:
            f.write(f"a = {a}")
            f.write(f"b = {b}")
            f.write(f"aa = {a @ a}")
            f.write(f"bb = {b @ b}")
            f.write(f"ab = {a @ b}")
        # raise MabCouldntSolve("Solved")
        return a, b

    # equations = list(sorted(equations, key=lambda f1: f"{f1}"))

    log.info(f"Looking for direct resolve")
    resolve_attempts: list[tuple[str, Field] | None] = [resolve_eq(eq, sym_classifier) for eq in equations]
    resolved: dict[str, Field] = {}
    for x in resolve_attempts:
        if x is None:
            continue
        v, f = x
        if v in resolved and resolved[v] != f:
            raise MabContradiction(f"{f} == {v} == {resolved[v]}")
        resolved[v] = f

    if len(resolved) > 0:
        log.info(f"Adding constraints: {[f'{v} = {resolved[v]}' for v in sorted(resolved.keys())]}")
        return mab_solve(rank, constraints | resolved, permissions_zero, permissions_nonzero, lastz_a, free_const_idx,
                         f"{progress_bar}_,")

    zgroup_attempts: list[tuple[str, Field] | None] = [check_zero_group(eq, sym_classifier) for eq in equations]
    zgroups = [zg for zg in zgroup_attempts if zg is not None]
    for zg in zgroups:
        for v in zg:
            try:
                log.warning(f"Trying {v} = 0")
                lastz_a_ = v.startswith("a")
                return mab_solve(rank, constraints, permissions_zero | {v}, permissions_nonzero, lastz_a_,
                                 free_const_idx, f"{progress_bar}{v}=0,")
            except MabContradiction as e:
                log.info(f"backtracking: {e}")
            except MabCouldntSolve as e:
                log.info(f"backtracking: {e}")

    linear_attempts = [check_linear(eq, sym_classifier) for eq in equations]
    lns = [ln for ln in linear_attempts if ln is not None]
    free_const = Field(f"r{free_const_idx}")
    free_const_idx += 1
    for c in [Field.Zero, Field.Unit]:
        for v, factor, fms in lns:
            try:
                log.info(f"Trying {v} = {c}")
                return mab_solve(rank, constraints | {v: c}, permissions_zero | {v}, permissions_nonzero, lastz_a,
                                 free_const_idx, f"{progress_bar}{v}={c},")
            except MabContradiction as e:
                log.info(f"backtracking: {e}")
            except MabCouldntSolve as e:
                log.info(f"backtracking: {e}")
    for v, factor, fms in lns:
        # for n in range(1, len(fms) + 1):
        for n in [1]:
            for cmb in itertools.combinations(fms, n):
                c = functools.reduce(lambda x, y: x + y, cmb, Field.Zero)
                try:
                    log.info(f"Trying {v} = {c}")
                    return mab_solve(rank, constraints | {v: c}, permissions_zero | {v}, permissions_nonzero, lastz_a,
                                     free_const_idx, f"{progress_bar}{v}=#,")
                except MabContradiction as e:
                    log.info(f"backtracking: {e}")
                except MabCouldntSolve as e:
                    log.info(f"backtracking: {e}")

    raise MabCouldntSolve()
