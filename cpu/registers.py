"""
cpu/registers.py — Register file for the 9-trit CPU.

General-purpose registers : R0 – R8   (R0 is hardwired to zero, writes ignored)
Special registers          : PC, FLAGS

FLAGS word layout (trits 8..0, MST first):
    trit 8  : sign   (N/Z/P — sign of last result)
    trit 7  : carry  (N/Z/P — carry/borrow from last arithmetic op)
    trit 6  : zero   (Z or P — 1 if last result was zero)
    trits 5-0 : reserved (always zero)
"""

from cpu.trits import Word, WORD_SIZE, Z, N, P, ZERO


# Register names exposed to the CPU
GP_REGS = [f"R{i}" for i in range(9)]   # R0 … R8
ALL_REGS = GP_REGS + ["PC", "FLAGS"]


class Registers:
    """
    Register file containing 9 general-purpose registers, a program counter,
    and a flags register.  All values are Words (9 trits).

    R0 is the zero register: reads always return 0, writes are silently ignored.
    """

    def __init__(self):
        self._regs: dict[str, Word] = {name: ZERO for name in ALL_REGS}

    # ── read / write ────────────────────────────────────────────────────────

    def read(self, name: str) -> Word:
        key = name.upper()
        if key not in self._regs:
            raise KeyError(f"Unknown register: '{name}'")
        return self._regs[key]

    def write(self, name: str, value) -> None:
        key = name.upper()
        if key not in self._regs:
            raise KeyError(f"Unknown register: '{name}'")
        if key == "R0":
            return        # R0 is hardwired zero
        if not isinstance(value, Word):
            value = Word(value)
        self._regs[key] = value

    # ── convenience properties ───────────────────────────────────────────────

    @property
    def pc(self) -> Word:
        return self._regs["PC"]

    @pc.setter
    def pc(self, value):
        self._regs["PC"] = value if isinstance(value, Word) else Word(value)

    @property
    def flags(self) -> Word:
        return self._regs["FLAGS"]

    # ── flag helpers ─────────────────────────────────────────────────────────

    def update_flags(self, flags: dict) -> None:
        """
        Update FLAGS from a dict returned by alu_execute.
        Expected keys: 'sign', 'carry', 'zero'.
        """
        trits = [Z] * WORD_SIZE
        trits[0] = flags.get("sign",  Z)
        trits[1] = flags.get("carry", Z)
        trits[2] = P if flags.get("zero", False) else Z
        self._regs["FLAGS"] = Word(trits)

    def flag_sign(self)  -> int:
        return self._regs["FLAGS"][0]

    def flag_carry(self) -> int:
        return self._regs["FLAGS"][1]

    def flag_zero(self)  -> bool:
        return self._regs["FLAGS"][2] == P

    # ── PC helpers ───────────────────────────────────────────────────────────

    def pc_advance(self, steps: int = 2) -> None:
        """Advance PC by *steps* (default 2 — one 18-trit instruction)."""
        from cpu.ternary import ternary_add
        new_pc, _ = ternary_add(self._regs["PC"], Word(steps))
        self._regs["PC"] = new_pc

    def pc_set(self, addr) -> None:
        self._regs["PC"] = addr if isinstance(addr, Word) else Word(addr)

    # ── display ──────────────────────────────────────────────────────────────

    def dump(self) -> None:
        print(f"{'Register':<8}  {'Trits':>9}  {'Value':>6}")
        print("-" * 30)
        for name in ALL_REGS:
            w = self._regs[name]
            print(f"{name:<8}  {str(w):>9}  {w.to_int():>6}")

    def __repr__(self):
        parts = [f"{n}={self._regs[n].to_int()}" for n in ALL_REGS]
        return "Registers(" + ", ".join(parts) + ")"
