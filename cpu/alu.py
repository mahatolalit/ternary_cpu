"""
cpu/alu.py — Arithmetic Logic Unit.

Exposes a single entry point:

    result, flags = alu_execute(op, a, b)

where
    op     : str  — operation name (see ALU_OPS below)
    a, b   : Word — operands  (b is ignored for unary ops)
    result : Word — computed result
    flags  : dict — {"sign": trit, "carry": trit, "zero": bool}

All flags are updated on every operation.

Supported operations
--------------------
Arithmetic  : ADD, SUB, MUL, NEG
Tritwise    : TAND, TOR, TMIN, TMAX, TADD, TMUL, TNEG, TABS
Comparison  : CMP   (returns -1/0/+1 as a Word, no carry)
"""

from cpu.trits import Word, Z, N, P
from cpu.ternary import (
    ternary_add, ternary_sub, ternary_mul, ternary_neg,
    trit_and, trit_or, trit_min, trit_max,
    trit_tadd, trit_tmul, trit_neg, trit_abs,
    trit_inc, trit_dec,
)


# ── Flag computation ────────────────────────────────────────────────────────

def _flags(result: Word, carry=Z) -> dict:
    return {
        "sign" : result.sign,     # MST of result: N, Z, or P
        "carry": carry,
        "zero" : result.is_zero(),
    }


# ── ALU dispatcher ─────────────────────────────────────────────────────────

def alu_execute(op: str, a: Word, b: Word = None):
    """
    Execute one ALU operation.

    Parameters
    ----------
    op : str   — operation name (case-insensitive)
    a  : Word  — first operand
    b  : Word  — second operand (required for binary ops, ignored for unary)

    Returns
    -------
    (result: Word, flags: dict)
    """
    op = op.upper()

    if op == "ADD":
        res, carry = ternary_add(a, b)
        return res, _flags(res, carry)

    elif op == "SUB":
        res, borrow = ternary_sub(a, b)
        return res, _flags(res, borrow)

    elif op == "MUL":
        res = ternary_mul(a, b)
        return res, _flags(res)

    elif op == "NEG":
        res = ternary_neg(a)
        return res, _flags(res)

    elif op == "TAND":
        res = trit_and(a, b)
        return res, _flags(res)

    elif op == "TOR":
        res = trit_or(a, b)
        return res, _flags(res)

    elif op == "TMIN":
        res = trit_min(a, b)
        return res, _flags(res)

    elif op == "TMAX":
        res = trit_max(a, b)
        return res, _flags(res)

    elif op == "TADD":
        res = trit_tadd(a, b)
        return res, _flags(res)

    elif op == "TMUL":
        res = trit_tmul(a, b)
        return res, _flags(res)

    elif op == "TNEG":
        res = trit_neg(a)
        return res, _flags(res)

    elif op == "TABS":
        res = trit_abs(a)
        return res, _flags(res)

    elif op == "TINC":
        res = trit_inc(a)
        return res, _flags(res)

    elif op == "TDEC":
        res = trit_dec(a)
        return res, _flags(res)

    elif op == "CMP":
        a_int = a.to_int()
        b_int = b.to_int()
        if a_int < b_int:
            res = Word(-1)
        elif a_int > b_int:
            res = Word(1)
        else:
            res = Word(0)
        return res, _flags(res)

    else:
        raise ValueError(f"Unknown ALU operation: '{op}'")


# ── Constants: all supported op names ──────────────────────────────────────
ALU_OPS = frozenset([
    "ADD", "SUB", "MUL", "NEG",
    "TAND", "TOR", "TMIN", "TMAX", "TADD", "TMUL", "TNEG", "TABS",
    "TINC", "TDEC", "CMP",
])
