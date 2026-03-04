"""
cpu/trits.py — Fundamental trit primitives and the Word type.

Each trit has one of three values:
    N = −1
    Z =  0
    P = +1

A *Word* is a fixed-width balanced-ternary integer: exactly WORD_SIZE trits.
Values range from −(3^9 − 1)//2 = −9841  to  +9841.

Tritwise gates are stored as compact lookup dicts so that every operation is
a simple table lookup — the same approach used in the tedkotz/ternary C
reference implementation.
"""

# ── Constants ──────────────────────────────────────────────────────────────
N, Z, P = -1, 0, 1          # canonical trit values
TRITS    = (N, Z, P)
WORD_SIZE = 9                # trits per word
WORD_MIN  = -(3**WORD_SIZE - 1) // 2   # −9841
WORD_MAX  =  (3**WORD_SIZE - 1) // 2   # +9841

# ── Symbol helpers ─────────────────────────────────────────────────────────
_TO_SYM   = {N: "-", Z: "0", P: "+"}
_FROM_SYM = {"-": N, "_": N, "n": N, "N": N,
             "0": Z, "z": Z, "Z": Z,
             "+": P, "1": P, "p": P, "P": P}


def trit_to_symbol(t: int) -> str:
    return _TO_SYM[t]


def symbol_to_trit(s: str) -> int:
    return _FROM_SYM[s]


def trit_str(trits) -> str:
    """Return display string for an iterable of trits, e.g. [1,0,-1] → '+0-'."""
    return "".join(_TO_SYM[t] for t in trits)


# ── Unary trit gate lookup  ────────────────────────────────────────────────
# Each gate is a dict {trit → trit}.
# Index convention: N=-1, Z=0, P=+1.

GATE1 = {
    # name   :  { N:?,  Z:?,  P:? }
    "INC"    : { N: Z,  Z: P,  P: N  },   # saturating +1 mod 3
    "DEC"    : { N: P,  Z: N,  P: Z  },   # saturating -1 mod 3
    "NEG"    : { N: P,  Z: Z,  P: N  },   # negate / flip sign
    "FLT"    : { N: N,  Z: Z,  P: Z  },   # floor: clamp positive to 0
    "ABS"    : { N: P,  Z: Z,  P: P  },   # absolute value
    "SGN"    : { N: N,  Z: Z,  P: P  },   # identity (sign)
    "LAX"    : { N: Z,  Z: Z,  P: P  },   # ceil-negative to 0
}

# ── Binary trit gate lookup  ───────────────────────────────────────────────
# Each gate is  dict { (a, b) → result_trit }
# a, b ∈ {N, Z, P}

def _g2(table):
    """Turn a 3×3 list-of-lists into a (a,b)→trit dict."""
    vals = [N, Z, P]
    return {(vals[r], vals[c]): table[r][c]
            for r in range(3) for c in range(3)}


# tables indexed [a_row][b_col] with rows/cols ordered N, Z, P

GATE2 = {
    #              b: N   Z   P
    "AND" : _g2([ [N,  N,  N],   # a=N
                  [N,  Z,  Z],   # a=Z
                  [N,  Z,  P] ]),# a=P

    "OR"  : _g2([ [N,  Z,  P],
                  [Z,  Z,  P],
                  [P,  P,  P] ]),

    "MIN" : _g2([ [N,  N,  N],
                  [N,  Z,  Z],
                  [N,  Z,  P] ]),

    "MAX" : _g2([ [N,  Z,  P],
                  [Z,  Z,  P],
                  [P,  P,  P] ]),

    # Tritwise addition (no carry)
    "TADD": _g2([ [P,  N,  Z],   # N+N→P(wrap), N+Z→N, N+P→Z
                  [N,  Z,  P],
                  [Z,  P,  N] ]),

    # Tritwise multiply (Galois / consensus)
    "TMUL": _g2([ [P,  Z,  N],
                  [Z,  Z,  Z],
                  [N,  Z,  P] ]),

    # Majority / carry computation
    "UNM" : _g2([ [N,  Z,  Z],
                  [Z,  Z,  Z],
                  [Z,  Z,  P] ]),
}


def apply_gate1(gate_name: str, t: int) -> int:
    """Apply a unary trit gate to a single trit."""
    return GATE1[gate_name][t]


def apply_gate2(gate_name: str, a: int, b: int) -> int:
    """Apply a binary trit gate to two single trits."""
    return GATE2[gate_name][(a, b)]


def apply_gate1_word(gate_name: str, word) -> list:
    """Apply unary gate trit-by-trit to a list of trits."""
    g = GATE1[gate_name]
    return [g[t] for t in word]


def apply_gate2_word(gate_name: str, a, b) -> list:
    """Apply binary gate trit-by-trit to two equal-length trit lists."""
    g = GATE2[gate_name]
    return [g[(ta, tb)] for ta, tb in zip(a, b)]


# ── Word class ─────────────────────────────────────────────────────────────

class Word:
    """
    A fixed-width balanced-ternary integer (WORD_SIZE = 9 trits).

    Internally stored as a tuple of ints in {−1, 0, +1},
    MST (most-significant trit) first.

    Construction:
        Word()               → all-zero word
        Word(42)             → from Python int
        Word([1, 0, -1, …])  → from trit list / tuple (must be ≤ 9 trits)
        Word(other_word)     → copy
    """

    __slots__ = ("_trits",)

    def __init__(self, value=0):
        if isinstance(value, Word):
            object.__setattr__(self, "_trits", value._trits)
        elif isinstance(value, (list, tuple)):
            trits = list(value)
            if len(trits) > WORD_SIZE:
                raise ValueError(f"Too many trits: {len(trits)} > {WORD_SIZE}")
            # left-pad with zeros
            padded = [Z] * (WORD_SIZE - len(trits)) + list(trits)
            if any(t not in TRITS for t in padded):
                raise ValueError(f"Invalid trit in sequence: {trits}")
            object.__setattr__(self, "_trits", tuple(padded))
        elif isinstance(value, int):
            if not (WORD_MIN <= value <= WORD_MAX):
                # wrap around (mod 3^9)
                period = 3 ** WORD_SIZE
                if value > WORD_MAX:
                    value -= period
                elif value < WORD_MIN:
                    value += period
            object.__setattr__(self, "_trits", tuple(_int_to_trits(value, WORD_SIZE)))
        else:
            raise TypeError(f"Cannot construct Word from {type(value)}")

    # make immutable
    def __setattr__(self, *_):
        raise AttributeError("Word is immutable")

    # ── trit access ────────────────────────────────────────────────────────

    def __getitem__(self, idx):
        return self._trits[idx]

    def __iter__(self):
        return iter(self._trits)

    def __len__(self):
        return WORD_SIZE

    def to_list(self) -> list:
        return list(self._trits)

    def to_int(self) -> int:
        return _trits_to_int(self._trits)

    @property
    def sign(self) -> int:
        """Most-significant non-zero trit, or 0."""
        for t in self._trits:
            if t != Z:
                return t
        return Z

    def is_zero(self) -> bool:
        return all(t == Z for t in self._trits)

    # ── representation ─────────────────────────────────────────────────────

    def __repr__(self):
        return f"Word({trit_str(self._trits)} | {self.to_int()})"

    def __str__(self):
        return trit_str(self._trits)

    # ── comparison ────────────────────────────────────────────────────────

    def __eq__(self, other):
        if isinstance(other, Word):
            return self._trits == other._trits
        if isinstance(other, int):
            return self.to_int() == other
        return NotImplemented

    def __lt__(self, other):
        return self.to_int() < (other.to_int() if isinstance(other, Word) else other)

    def __hash__(self):
        return hash(self._trits)

    # ── arithmetic passthrough (delegates to ternary module) ───────────────
    # (avoid circular imports — arithmetic wraps Word operations)


# ── Internal helpers ───────────────────────────────────────────────────────

def _int_to_trits(n: int, width: int) -> list:
    """Convert a Python int to a balanced-ternary list of *width* trits (MST first)."""
    trits = []
    for _ in range(width):
        r = n % 3
        n //= 3
        if r == 2:
            r = -1
            n += 1
        trits.append(r)
    return trits[::-1]   # MST first


def _trits_to_int(trits) -> int:
    """Convert an iterable of trits (MST first) to a Python int."""
    v = 0
    for t in trits:
        v = v * 3 + t
    return v


# ── Convenience constructors ───────────────────────────────────────────────

ZERO  = Word(0)
ONE   = Word(1)
NEG1  = Word(-1)
