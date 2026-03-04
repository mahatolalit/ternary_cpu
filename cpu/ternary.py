"""
cpu/ternary.py — Balanced-ternary arithmetic on Word objects.

All functions accept and return Word instances (or ints where noted).

Key operations:
    ternary_add(a, b)       → (Word, carry_trit)   full adder
    ternary_sub(a, b)       → (Word, borrow_trit)
    ternary_mul(a, b)       → Word  (lower 9 trits)
    ternary_shift(a, n)     → Word  (n>0 left, n<0 right, in trits)
    to_word(n)              → Word  from int
    from_word(w)            → int
"""

from cpu.trits import (
    Word, WORD_SIZE, ZERO,
    N, Z, P, TRITS,
    GATE1, GATE2,
    apply_gate2_word, apply_gate1_word,
    _int_to_trits, _trits_to_int,
)


# ── Conversion helpers ─────────────────────────────────────────────────────

def to_word(n: int) -> Word:
    """Convert a Python int to a 9-trit Word (wraps on overflow)."""
    return Word(n)


def from_word(w) -> int:
    """Convert a Word (or trit list) to a Python int."""
    if isinstance(w, Word):
        return w.to_int()
    return _trits_to_int(w)


def trit_str(w) -> str:
    """Human-readable trit string like '+0-+0++0-'."""
    syms = {-1: "-", 0: "0", 1: "+"}
    return "".join(syms[t] for t in w)


# ── Core arithmetic ────────────────────────────────────────────────────────

def _add_lists(a_trits: list, b_trits: list):
    """
    Ripple-carry adder on two WORD_SIZE trit lists.
    Uses the carry-propagation loop from the tedkotz reference:
        carry_out  = UNM(a, b)          (majority)
        sum_no_carry = TADD(a, b)       (trit XOR)
    Repeats until no carry.

    Returns (result_list, carry_trit).
    """
    g_tadd = GATE2["TADD"]
    g_unm  = GATE2["UNM"]

    result = list(a_trits)
    addend = list(b_trits)
    carry_out = Z      # single carry trit out of MST

    # propagate until nothing left to add
    while any(t != Z for t in addend):
        carries = [g_unm[(result[i], addend[i])] for i in range(WORD_SIZE)]
        result  = [g_tadd[(result[i], addend[i])] for i in range(WORD_SIZE)]
        # shift carries left by one trit position
        carry_out = carries[0]
        addend = carries[1:] + [Z]

    return result, carry_out


def ternary_add(a, b):
    """
    Add two Words.
    Returns (Word result, carry_trit) where carry_trit ∈ {−1, 0, +1}.
    """
    a_t = list(a) if isinstance(a, Word) else list(Word(a))
    b_t = list(b) if isinstance(b, Word) else list(Word(b))
    res, carry = _add_lists(a_t, b_t)
    return Word(res), carry


def ternary_sub(a, b):
    """
    Subtract b from a  (a − b).
    Returns (Word result, borrow_trit).
    Implemented as a + (−b).
    """
    b_neg_t = apply_gate1_word("NEG", list(b) if isinstance(b, Word) else list(Word(b)))
    a_t     = list(a) if isinstance(a, Word) else list(Word(a))
    res, carry = _add_lists(a_t, b_neg_t)
    return Word(res), carry


def ternary_neg(a) -> Word:
    """Negate a Word (arithmetic negation, i.e. flip every trit)."""
    trits = list(a) if isinstance(a, Word) else list(Word(a))
    return Word(apply_gate1_word("NEG", trits))


def ternary_mul(a, b) -> Word:
    """
    Multiply two Words using shift-and-add.
    Result is truncated to WORD_SIZE trits (lower portion).
    """
    a_t = list(a) if isinstance(a, Word) else list(Word(a))
    b_t = list(b) if isinstance(b, Word) else list(Word(b))

    product = [Z] * WORD_SIZE
    # iterate over b LST first
    for i in range(WORD_SIZE - 1, -1, -1):
        trit = b_t[i]
        if trit == Z:
            continue
        # shift a_t left by (WORD_SIZE - 1 - i) positions
        shift = WORD_SIZE - 1 - i
        shifted = a_t[shift:] + [Z] * shift  # left-shift truncating high trits

        if trit == N:
            # subtract: negate shifted, then add
            neg_shifted = apply_gate1_word("NEG", shifted)
            product, _ = _add_lists(product, neg_shifted)
        else:
            product, _ = _add_lists(product, shifted)

    return Word(product)


def ternary_shift(a, n: int) -> Word:
    """
    Trit shift.  n > 0 → left (multiply by 3^n), n < 0 → right (divide by 3^|n|).
    Vacated positions are filled with zeros.  Bits shifted out are discarded.
    """
    trits = list(a) if isinstance(a, Word) else list(Word(a))
    if n == 0:
        return Word(trits)
    if n > 0:
        shifted = trits[n:] + [Z] * n          # left shift
    else:
        shifted = [Z] * (-n) + trits[:n]       # right shift  (n is negative)
    return Word(shifted[:WORD_SIZE])


# ── Tritwise logical operations  ───────────────────────────────────────────

def trit_and(a, b)  -> Word:
    return Word(apply_gate2_word("AND",  list(a), list(b)))

def trit_or(a, b)   -> Word:
    return Word(apply_gate2_word("OR",   list(a), list(b)))

def trit_min(a, b)  -> Word:
    return Word(apply_gate2_word("MIN",  list(a), list(b)))

def trit_max(a, b)  -> Word:
    return Word(apply_gate2_word("MAX",  list(a), list(b)))

def trit_tadd(a, b) -> Word:
    """Tritwise addition (no carry — Galois-field addition mod 3)."""
    return Word(apply_gate2_word("TADD", list(a), list(b)))

def trit_tmul(a, b) -> Word:
    """Tritwise multiplication (Galois-field multiply mod 3)."""
    return Word(apply_gate2_word("TMUL", list(a), list(b)))

def trit_neg(a)     -> Word:
    return Word(apply_gate1_word("NEG",  list(a)))

def trit_abs(a)     -> Word:
    return Word(apply_gate1_word("ABS",  list(a)))

def trit_inc(a)     -> Word:
    return Word(apply_gate1_word("INC",  list(a)))

def trit_dec(a)     -> Word:
    return Word(apply_gate1_word("DEC",  list(a)))
