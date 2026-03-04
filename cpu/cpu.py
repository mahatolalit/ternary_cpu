"""
cpu/cpu.py — 9-trit balanced-ternary CPU emulator.

Instruction encoding (18 trits = 2 consecutive 9-trit memory words)
────────────────────────────────────────────────────────────────────
  memory[PC + 0]  =  high word:  [ op2 op1 op0 | ra1 ra0 | rb1 rb0 | fl1 fl0 ]
                                   ─── opcode ──  ── RA ──  ── RB ──  ─ flags ─
  memory[PC + 1]  =  low  word:  [ imm8 imm7 … imm0 ]

Trit positions within the high word (index 0 = MST):
    [0..2]  opcode  (3 trits → 27 possible opcodes)
    [3..4]  RA      (2 trits → encodes R0–R8 via ternary index)
    [5..6]  RB      (2 trits)
    [7..8]  flags   (2 trits, instruction-specific modifiers)

Register encoding (2 trits, balanced ternary)
    −4 → R0,  −3 → R1,  −2 → R2,  −1 → R3
     0 → R4,   1 → R5,   2 → R6,   3 → R7
     4 → R8

     (Minimum 2-trit value = 3^0*(-1)+3^1*(-1) = -4, maximum = +4)

Opcode table (stored as the 3-trit balanced-ternary integer)
    value  mnemonic  description
    ──────────────────────────────────────────────────────────
      0    NOP       no operation
      1    MOV       RA ← imm
      2    ADD       RA ← RA + RB
      3    SUB       RA ← RA − RB
      4    NEG       RA ← −RA
      5    LOAD      RA ← MEM[RB + imm]
      6    STORE     MEM[RA + imm] ← RB
      7    JMP       PC ← imm
      8    JZ        if zero-flag: PC ← imm
      9    JNZ       if not zero-flag: PC ← imm
     10    TAND      RA ← RA AND RB  (tritwise)
     11    TOR       RA ← RA OR  RB  (tritwise)
     12    TMUL      RA ← RA *   RB  (tritwise Galois)
     13    MUL       RA ← RA ×   RB  (arithmetic)
     -13   HALT      stop execution
"""

from cpu.trits   import Word, ZERO, Z, N, P, WORD_SIZE
from cpu.ternary import ternary_add, ternary_sub, from_word, to_word
from cpu.alu     import alu_execute
from cpu.registers import Registers
from cpu.memory    import Memory, ADDR_MIN


# ── Opcode definitions ─────────────────────────────────────────────────────

class Opcode:
    NOP   =  0
    MOV   =  1
    ADD   =  2
    SUB   =  3
    NEG   =  4
    LOAD  =  5
    STORE =  6
    JMP   =  7
    JZ    =  8
    JNZ   =  9
    TAND  =  10
    TOR   =  11
    TMUL  =  12
    MUL   =  13
    HALT  = -13   # 3-trit value of -13  ↔  trits [−,−,−]


# ── Register index encoding/decoding ──────────────────────────────────────
# 2-trit balanced ternary: range −4…+4, 9 values → R0…R8

def _reg_from_index(idx: int) -> str:
    """Convert 2-trit integer (−4…+4) to register name 'R0'…'R8'."""
    reg_num = idx + 4        # shift: 0…8
    if not (0 <= reg_num <= 8):
        raise ValueError(f"Register index {idx} out of range")
    return f"R{reg_num}"


def _reg_to_index(name: str) -> int:
    """Convert register name 'R0'…'R8' to 2-trit integer (−4…+4)."""
    n = int(name[1:])
    if not (0 <= n <= 8):
        raise ValueError(f"Invalid register name: {name}")
    return n - 4


def _encode_reg(name: str) -> list:
    """Return 2-element trit list encoding for a register name."""
    idx = _reg_to_index(name)
    # 2-trit balanced ternary encoding
    t1 = N if idx < -3 else (P if idx > 3 else Z)
    remainder = idx - (t1 * 3)
    t0 = N if remainder < 0 else (P if remainder > 0 else Z)
    # Manual: idx = t1*3 + t0
    t1 = idx // 3
    t0 = idx - t1 * 3
    if t0 > 1:
        t0 -= 3; t1 += 1
    elif t0 < -1:
        t0 += 3; t1 -= 1
    return [t1, t0]


def _decode_reg(trits: list) -> str:
    """Convert 2-element trit list to register name."""
    idx = trits[0] * 3 + trits[1]
    return _reg_from_index(idx)


# ── Instruction encoding / decoding ───────────────────────────────────────

class Instruction:
    """Decoded instruction from an 18-trit word pair."""
    __slots__ = ("opcode", "ra", "rb", "flags", "imm")

    def __init__(self, opcode: int, ra: str, rb: str, flags: int, imm: Word):
        self.opcode = opcode    # int
        self.ra     = ra        # str  e.g. "R3"
        self.rb     = rb        # str
        self.flags  = flags     # int
        self.imm    = imm       # Word

    def __repr__(self):
        return (f"Instruction(op={self.opcode}, ra={self.ra}, rb={self.rb}, "
                f"flags={self.flags}, imm={self.imm.to_int()})")


def decode_instruction(high: Word, low: Word) -> Instruction:
    """
    Decode two 9-trit Words into an Instruction.

    high = memory[PC]    : [op2 op1 op0 | ra1 ra0 | rb1 rb0 | fl1 fl0]
    low  = memory[PC+1]  : [imm8 … imm0]
    """
    t = list(high)
    opcode = Word(t[0:3]).to_int()
    ra     = _decode_reg(t[3:5])
    rb     = _decode_reg(t[5:7])
    flags  = Word(t[7:9]).to_int()
    imm    = low
    return Instruction(opcode, ra, rb, flags, imm)


def encode_instruction(opcode: int, ra: str = "R0", rb: str = "R0",
                       flags: int = 0, imm: int = 0):
    """
    Encode an instruction into two 9-trit Words.
    Returns (high_word, low_word).
    """
    op_trits  = list(Word(opcode))            # 9 trits, but we only need 3
    ra_trits  = _encode_reg(ra)               # 2 trits
    rb_trits  = _encode_reg(rb)               # 2 trits
    fl_trits  = list(Word(flags))[7:9]        # 2 trits (LST 2 of 9)
    imm_word  = Word(imm)

    # take only the 3 least-significant trits of opcode
    high_trits = op_trits[6:9] + ra_trits + rb_trits + fl_trits
    high = Word(high_trits)
    return high, imm_word


# ── Mnemonic → opcode / opcode → mnemonic  ────────────────────────────────

_MNEMONIC_TO_OPCODE = {
    "NOP": 0, "MOV": 1, "ADD": 2, "SUB": 3, "NEG": 4,
    "LOAD": 5, "STORE": 6, "JMP": 7, "JZ": 8, "JNZ": 9,
    "TAND": 10, "TOR": 11, "TMUL": 12, "MUL": 13, "HALT": -13,
}
_OPCODE_TO_MNEMONIC = {v: k for k, v in _MNEMONIC_TO_OPCODE.items()}


def mnemonic(opcode: int) -> str:
    return _OPCODE_TO_MNEMONIC.get(opcode, f"OP({opcode})")


# ── CPU class ──────────────────────────────────────────────────────────────

class CPU:
    """
    9-trit balanced-ternary CPU emulator.

    Usage
    -----
    cpu = CPU()
    cpu.load_program(words, start_addr=ADDR_MIN)
    cpu.run()          # runs until HALT or max_cycles
    cpu.registers.dump()
    cpu.memory.dump()
    """

    def __init__(self):
        self.registers = Registers()
        self.memory    = Memory()
        self.running   = False
        self.cycle     = 0

    def reset(self):
        self.registers = Registers()
        self.running   = False
        self.cycle     = 0

    # ── program loading ───────────────────────────────────────────────────

    def load_program(self, words, start_addr: int = ADDR_MIN) -> None:
        """Load a flat list of ints/Words into memory and set PC to start_addr."""
        self.memory.load(words, start_addr)
        self.registers.pc_set(start_addr)

    # ── fetch / decode ────────────────────────────────────────────────────

    def fetch(self) -> Instruction:
        pc  = self.registers.pc
        pc_int = pc.to_int()
        high   = self.memory.read(pc_int)
        low    = self.memory.read(pc_int + 1)
        self.registers.pc_advance(2)
        return decode_instruction(high, low)

    # ── execute ───────────────────────────────────────────────────────────

    def execute(self, inst: Instruction) -> None:
        regs = self.registers
        mem  = self.memory
        op   = inst.opcode
        ra, rb, imm = inst.ra, inst.rb, inst.imm

        if op == Opcode.NOP:
            pass

        elif op == Opcode.HALT:
            self.running = False

        elif op == Opcode.MOV:
            regs.write(ra, imm)
            regs.update_flags({"sign": imm.sign, "carry": Z, "zero": imm.is_zero()})

        elif op == Opcode.ADD:
            a_val = regs.read(ra)
            b_val = regs.read(rb)
            result, flags = alu_execute("ADD", a_val, b_val)
            regs.write(ra, result)
            regs.update_flags(flags)

        elif op == Opcode.SUB:
            a_val = regs.read(ra)
            b_val = regs.read(rb)
            result, flags = alu_execute("SUB", a_val, b_val)
            regs.write(ra, result)
            regs.update_flags(flags)

        elif op == Opcode.NEG:
            a_val = regs.read(ra)
            result, flags = alu_execute("NEG", a_val)
            regs.write(ra, result)
            regs.update_flags(flags)

        elif op == Opcode.LOAD:
            # RA ← MEM[RB + imm]
            base   = regs.read(rb).to_int()
            offset = imm.to_int()
            val    = mem.read(base + offset)
            regs.write(ra, val)
            regs.update_flags({"sign": val.sign, "carry": Z, "zero": val.is_zero()})

        elif op == Opcode.STORE:
            # MEM[RA + imm] ← RB
            base   = regs.read(ra).to_int()
            offset = imm.to_int()
            val    = regs.read(rb)
            mem.write(base + offset, val)
            regs.update_flags({"sign": val.sign, "carry": Z, "zero": val.is_zero()})

        elif op == Opcode.JMP:
            regs.pc_set(imm.to_int())

        elif op == Opcode.JZ:
            if regs.flag_zero():
                regs.pc_set(imm.to_int())

        elif op == Opcode.JNZ:
            if not regs.flag_zero():
                regs.pc_set(imm.to_int())

        elif op == Opcode.TAND:
            result, flags = alu_execute("TAND", regs.read(ra), regs.read(rb))
            regs.write(ra, result)
            regs.update_flags(flags)

        elif op == Opcode.TOR:
            result, flags = alu_execute("TOR", regs.read(ra), regs.read(rb))
            regs.write(ra, result)
            regs.update_flags(flags)

        elif op == Opcode.TMUL:
            result, flags = alu_execute("TMUL", regs.read(ra), regs.read(rb))
            regs.write(ra, result)
            regs.update_flags(flags)

        elif op == Opcode.MUL:
            result, flags = alu_execute("MUL", regs.read(ra), regs.read(rb))
            regs.write(ra, result)
            regs.update_flags(flags)

        else:
            raise ValueError(f"Unknown opcode: {op} at cycle {self.cycle}")

    # ── run loop ──────────────────────────────────────────────────────────

    def run(self, max_cycles: int = 100_000, trace: bool = False) -> int:
        """
        Run until HALT or *max_cycles* executed.
        Returns the number of cycles executed.
        If *trace* is True, prints each instruction before executing.
        """
        self.running = True
        self.cycle   = 0

        while self.running and self.cycle < max_cycles:
            inst = self.fetch()
            if trace:
                pc_before = self.registers.pc.to_int() - 2
                print(f"  [{self.cycle:5d}] PC={pc_before:+4d}  "
                      f"{mnemonic(inst.opcode):<6} {inst.ra} {inst.rb} "
                      f"imm={inst.imm.to_int():+d}")
            self.execute(inst)
            self.cycle += 1

        if self.cycle >= max_cycles and self.running:
            print(f"Warning: max_cycles ({max_cycles}) reached without HALT")

        return self.cycle

    # ── convenience display ───────────────────────────────────────────────

    def state(self) -> None:
        """Print full CPU state."""
        print(f"\n{'═'*40}")
        print(f"  CPU state after {self.cycle} cycle(s)")
        print(f"{'═'*40}")
        self.registers.dump()
        print()
