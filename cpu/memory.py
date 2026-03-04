"""
cpu/memory.py — 729-cell balanced-ternary memory.

Address space : −364 … +364  (729 = 3^6 cells)
Cell width    : 9 trits (one Word)

Addresses are Python ints or Words; the range is validated on every access.
Uninitialized cells read as zero.
"""

from cpu.trits import Word, ZERO

MEMORY_SIZE  = 3 ** 6          # 729 cells
ADDR_MIN     = -(MEMORY_SIZE - 1) // 2   # −364
ADDR_MAX     =  (MEMORY_SIZE - 1) // 2   # +364


def _addr_to_key(addr) -> int:
    """Normalize address to a Python int and validate range."""
    if isinstance(addr, Word):
        addr = addr.to_int()
    if not (ADDR_MIN <= addr <= ADDR_MAX):
        raise IndexError(
            f"Memory address {addr} out of range [{ADDR_MIN}, {ADDR_MAX}]"
        )
    return addr


class Memory:
    """
    Flat 729-cell balanced-ternary memory.

    Each cell stores exactly one Word (9 trits).
    Unwritten cells return the zero Word.
    """

    def __init__(self):
        # sparse dict; addresses outside the dict return ZERO
        self._cells: dict[int, Word] = {}

    # ── basic access ────────────────────────────────────────────────────────

    def read(self, addr) -> Word:
        """Return the Word stored at *addr* (or zero if never written)."""
        return self._cells.get(_addr_to_key(addr), ZERO)

    def write(self, addr, value) -> None:
        """Write *value* (int or Word) to *addr*."""
        key = _addr_to_key(addr)
        if not isinstance(value, Word):
            value = Word(value)
        self._cells[key] = value

    # ── program loading ──────────────────────────────────────────────────────

    def load(self, words, start_addr: int = ADDR_MIN) -> None:
        """
        Load a sequence of ints or Words into memory starting at *start_addr*.

        Words are placed at start_addr, start_addr+1, start_addr+2, …
        """
        addr = start_addr
        for w in words:
            self.write(addr, w)
            addr += 1

    # ── display ──────────────────────────────────────────────────────────────

    def dump(self, lo: int = ADDR_MIN, hi: int = ADDR_MAX) -> None:
        """Print non-zero cells in the address range [lo, hi]."""
        print(f"{'Addr':>6}  {'Trits':>9}  {'Value':>6}")
        print("-" * 28)
        for addr in range(lo, hi + 1):
            w = self._cells.get(addr)
            if w is not None:
                print(f"{addr:>6}  {str(w):>9}  {w.to_int():>6}")

    def __repr__(self):
        n = len(self._cells)
        return f"Memory({n} non-zero cell{'s' if n != 1 else ''} / {MEMORY_SIZE} total)"
