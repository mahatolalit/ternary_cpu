"""
main.py — Unit tests and integration demo for the 9-trit CPU.

Run:
    python main.py
"""

from cpu.trits   import Word, WORD_SIZE, WORD_MIN, WORD_MAX, N, Z, P, trit_str
from cpu.ternary import (
    to_word, from_word, ternary_add, ternary_sub, ternary_mul,
    ternary_neg, ternary_shift,
    trit_and, trit_or, trit_min, trit_max, trit_tadd, trit_tmul,
)
from cpu.alu      import alu_execute
from cpu.registers import Registers
from cpu.memory    import Memory, ADDR_MIN, ADDR_MAX
from cpu.cpu       import CPU, encode_instruction, Opcode



# ── helpers ────────────────────────────────────────────────────────────────

PASS = "✓"
FAIL = "✗"
_failures = []

def _check(label, got, expected):
    ok = (got == expected)
    status = PASS if ok else FAIL
    print(f"  {status}  {label}")
    if not ok:
        print(f"       got {got!r}, expected {expected!r}")
        _failures.append(label)

def section(title):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}")


# ── 1. Word / trit primitives ──────────────────────────────────────────────

section("1. Word — construction & conversion")

w = Word(0)
_check("Word(0).to_int() == 0",      w.to_int(), 0)
_check("Word(0).is_zero()",          w.is_zero(), True)

w = Word(9841)
_check("Word(9841).to_int() == 9841", w.to_int(), 9841)

w = Word(-9841)
_check("Word(-9841).to_int() == -9841", w.to_int(), -9841)

w = Word([P, Z, N])   # + 0 - = 9*1 + 3*0 + (-1) = 8
_check("Word([+,0,-]) == 8",         w.to_int(), 8)

w = Word(42)
_check("str(Word(42)) length == 9",  len(str(w)), WORD_SIZE)
_check("Word round-trip 42",         from_word(w), 42)

_check("WORD_MIN = -9841", WORD_MIN, -9841)
_check("WORD_MAX = +9841", WORD_MAX,  9841)


# ── 2. Trit display ────────────────────────────────────────────────────────

section("2. Trit symbol helpers")

_check("trit_str(Word(0))",  trit_str(Word(0)),  "000000000")
_check("trit_str(Word(1))",  trit_str(Word(1)),  "00000000+")
_check("trit_str(Word(-1))", trit_str(Word(-1)), "00000000-")


# ── 3. Ternary arithmetic ──────────────────────────────────────────────────

section("3. ternary_add")

for a_int, b_int in [(0, 0), (1, 1), (5, -3), (-9841, 9841), (100, -100)]:
    res, carry = ternary_add(Word(a_int), Word(b_int))
    expected   = a_int + b_int
    if WORD_MIN <= expected <= WORD_MAX:
        _check(f"add({a_int},{b_int}) no wrap", res.to_int(), expected)

section("3. ternary_sub")

for a_int, b_int in [(5, 3), (0, 0), (9841, 9841), (-5, -3)]:
    res, _ = ternary_sub(Word(a_int), Word(b_int))
    expected = a_int - b_int
    if WORD_MIN <= expected <= WORD_MAX:
        _check(f"sub({a_int},{b_int})", res.to_int(), expected)

section("3. ternary_neg")

for v in [0, 1, -1, 9841, -9841, 42]:
    res = ternary_neg(Word(v))
    _check(f"neg({v}) == {-v}", res.to_int(), -v)

section("3. ternary_mul")

for a_int, b_int in [(0, 5), (1, 7), (3, 3), (-2, 4), (10, -10)]:
    res = ternary_mul(Word(a_int), Word(b_int))
    expected = a_int * b_int
    if WORD_MIN <= expected <= WORD_MAX:
        _check(f"mul({a_int},{b_int}) == {expected}", res.to_int(), expected)

section("3. ternary_shift")

_check("shift(1, +1) == 3",  ternary_shift(Word(1),  1).to_int(), 3)
_check("shift(1, +2) == 9",  ternary_shift(Word(1),  2).to_int(), 9)
_check("shift(9, -1) == 3",  ternary_shift(Word(9), -1).to_int(), 3)


# ── 4. Tritwise logical ops ────────────────────────────────────────────────

section("4. Tritwise operations")

a = Word([P, Z, N])   # + 0 -
b = Word([N, Z, P])   # - 0 +

# Word([P,Z,N]) is left-padded to 9 trits: indices 6,7,8 hold P,Z,N.
# Check index 6 (first significant trit) rather than 0 (padded zero).
and_r = trit_and(a, b)
_check("TAND([+0-], [-0+]) first sig trit == -", and_r[6], N)
_check("TAND middle sig trit == 0",              and_r[7], Z)

or_r = trit_or(a, b)
_check("TOR([+0-], [-0+]) first sig trit == +",  or_r[6], P)

min_r = trit_min(a, b)
_check("TMIN first sig trit == min(+,-) = -",    min_r[6], N)

max_r = trit_max(a, b)
_check("TMAX first sig trit == max(+,-) = +",    max_r[6], P)

tadd_r = trit_tadd(Word(1), Word(1))
_check("TADD(1,1) LST = -1 (wrap)",   tadd_r[-1], N)

tmul_r = trit_tmul(Word([-1]), Word([-1]))
_check("TMUL(-,-) LST = +1",          tmul_r[-1], P)


# ── 5. ALU ─────────────────────────────────────────────────────────────────

section("5. ALU execute")

res, flags = alu_execute("ADD", Word(5), Word(3))
_check("ALU ADD(5,3) == 8",   res.to_int(), 8)
_check("ADD flags sign == +", flags["sign"], P)
_check("ADD flags zero == F", flags["zero"], False)

res, flags = alu_execute("SUB", Word(5), Word(5))
_check("ALU SUB(5,5) == 0",   res.to_int(), 0)
_check("SUB flags zero == T", flags["zero"], True)

res, _ = alu_execute("MUL", Word(3), Word(4))
_check("ALU MUL(3,4) == 12",  res.to_int(), 12)

res, _ = alu_execute("NEG", Word(7))
_check("ALU NEG(7) == -7",    res.to_int(), -7)

res, _ = alu_execute("CMP", Word(3), Word(5))
_check("CMP(3,5) == -1",      res.to_int(), -1)

res, _ = alu_execute("CMP", Word(5), Word(5))
_check("CMP(5,5) == 0",       res.to_int(), 0)


# ── 6. Registers ───────────────────────────────────────────────────────────

section("6. Registers")

regs = Registers()
_check("initial R0 == 0",  regs.read("R0").to_int(), 0)
_check("initial PC == 0",  regs.pc.to_int(), 0)

regs.write("R1", Word(42))
_check("R1 after write == 42",    regs.read("R1").to_int(), 42)

regs.write("R0", Word(99))
_check("R0 stays 0 (hardwired)",  regs.read("R0").to_int(), 0)

regs.update_flags({"sign": N, "carry": P, "zero": False})
_check("flag_sign == N",   regs.flag_sign(), N)
_check("flag_carry == P",  regs.flag_carry(), P)
_check("flag_zero == F",   regs.flag_zero(), False)

regs.pc_advance(2)
_check("pc_advance(2)",    regs.pc.to_int(), 2)


# ── 7. Memory ──────────────────────────────────────────────────────────────

section("7. Memory")

mem = Memory()
_check("unwritten cell == 0",   mem.read(0).to_int(), 0)

mem.write(0, Word(7))
_check("write/read 7 at addr 0", mem.read(0).to_int(), 7)

mem.write(ADDR_MIN, Word(-9841))
_check("write/read at ADDR_MIN", mem.read(ADDR_MIN).to_int(), -9841)

mem.write(ADDR_MAX, Word(1))
_check("write/read at ADDR_MAX", mem.read(ADDR_MAX).to_int(), 1)

try:
    mem.read(ADDR_MAX + 1)
    _check("out-of-range raises IndexError", False, True)
except IndexError:
    _check("out-of-range raises IndexError", True, True)


# ── 8. Instruction encode / decode ─────────────────────────────────────────

section("8. Instruction encode/decode")

from cpu.cpu import decode_instruction

h, l = encode_instruction(Opcode.MOV, ra="R3", imm=42)
inst = decode_instruction(h, l)
_check("decode opcode == MOV", inst.opcode, Opcode.MOV)
_check("decode RA == R3",      inst.ra, "R3")
_check("decode imm == 42",     inst.imm.to_int(), 42)

h, l = encode_instruction(Opcode.ADD, ra="R1", rb="R2")
inst = decode_instruction(h, l)
_check("decode opcode == ADD", inst.opcode, Opcode.ADD)
_check("decode RA == R1",      inst.ra, "R1")
_check("decode RB == R2",      inst.rb, "R2")

h, l = encode_instruction(Opcode.HALT)
inst = decode_instruction(h, l)
_check("decode HALT",          inst.opcode, Opcode.HALT)


# ── 9. Full CPU integration ────────────────────────────────────────────────

section("9. CPU — MOV + HALT")

cpu = CPU()
prog = []
h, l = encode_instruction(Opcode.MOV, ra="R1", imm=99)
prog += [h, l]
h, l = encode_instruction(Opcode.HALT)
prog += [h, l]
cpu.load_program(prog, ADDR_MIN)
cpu.run()
_check("CPU MOV R1,99 → R1 == 99", cpu.registers.read("R1").to_int(), 99)

section("9. CPU — ADD")

cpu = CPU()
prog = []
for op, ra, rb, imm in [
    (Opcode.MOV, "R1", "R0", 15),
    (Opcode.MOV, "R2", "R0",  7),
]:
    h, l = encode_instruction(op, ra=ra, rb=rb, imm=imm)
    prog += [h, l]
h, l = encode_instruction(Opcode.ADD, ra="R1", rb="R2")
prog += [h, l]
h, l = encode_instruction(Opcode.HALT)
prog += [h, l]
cpu.load_program(prog, ADDR_MIN)
cpu.run()
_check("CPU ADD 15+7 → R1 == 22", cpu.registers.read("R1").to_int(), 22)

section("9. CPU — countdown loop")

from examples.countdown import build_countdown

cpu = CPU()
cpu.load_program(build_countdown(5), ADDR_MIN)
cpu.run()
_check("countdown(5): R1 == 0", cpu.registers.read("R1").to_int(), 0)

section("9. CPU — LOAD / STORE")

cpu = CPU()
prog = []
for op, ra, rb, imm in [
    (Opcode.MOV,   "R1", "R0", 77),   # R1 = 77
    (Opcode.MOV,   "R2", "R0",  0),   # R2 = 0  (base address)
    (Opcode.STORE, "R2", "R1",  0),   # MEM[R2+0] ← R1
    (Opcode.MOV,   "R3", "R0",  0),   # R3 = 0  (clear)
    (Opcode.LOAD,  "R3", "R2",  0),   # R3 ← MEM[R2+0]
]:
    h, l = encode_instruction(op, ra=ra, rb=rb, imm=imm)
    prog += [h, l]
h, l = encode_instruction(Opcode.HALT)
prog += [h, l]
cpu.load_program(prog, ADDR_MIN)
cpu.run()
_check("LOAD/STORE round-trip: R3 == 77", cpu.registers.read("R3").to_int(), 77)


# ── Summary ────────────────────────────────────────────────────────────────

print(f"\n{'═'*50}")
if _failures:
    print(f"  FAILED: {len(_failures)} check(s):")
    for f in _failures:
        print(f"    ✗  {f}")
else:
    print(f"  All checks passed ✓")
print(f"{'═'*50}\n")