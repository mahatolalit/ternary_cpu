"""
examples/countdown.py
=====================
Demo: count down from 5 to 0 using the 9-trit CPU.

Assembly (pseudo):
    MOV  R1, 5       ; load counter
    MOV  R2, 1       ; load step
LOOP:
    SUB  R1, R2      ; counter -= 1
    JNZ  R1, LOOP    ; repeat while counter != 0
    HALT

Each instruction occupies 2 consecutive memory cells (18 trits).
The program is loaded at the base of memory (address −364).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cpu.cpu    import CPU, encode_instruction, Opcode
from cpu.memory import ADDR_MIN


def build_countdown(start: int = 5) -> list:
    """
    Assemble the countdown program.
    Returns a flat list of Words (high-word, low-word pairs).
    """
    base = ADDR_MIN   # −364: where the program starts

    # Instruction addresses (each instruction = 2 words)
    addr_mov_r1   = base + 0    # −364
    addr_mov_r2   = base + 2    # −362
    addr_sub      = base + 4    # −360   ← LOOP target
    addr_jnz      = base + 6    # −358
    addr_halt     = base + 8    # −356

    loop_target = addr_sub       # JNZ jumps back here

    program = []

    # MOV R1, start
    h, l = encode_instruction(Opcode.MOV, ra="R1", imm=start)
    program += [h, l]

    # MOV R2, 1
    h, l = encode_instruction(Opcode.MOV, ra="R2", imm=1)
    program += [h, l]

    # LOOP: SUB R1, R2
    h, l = encode_instruction(Opcode.SUB, ra="R1", rb="R2")
    program += [h, l]

    # JNZ R1, loop_target
    h, l = encode_instruction(Opcode.JNZ, ra="R1", imm=loop_target)
    program += [h, l]

    # HALT
    h, l = encode_instruction(Opcode.HALT)
    program += [h, l]

    return program


def run_countdown(start: int = 5, trace: bool = True):
    print(f"╔══════════════════════════════╗")
    print(f"║  Countdown from {start:<3}           ║")
    print(f"╚══════════════════════════════╝\n")

    cpu = CPU()
    program = build_countdown(start)
    cpu.load_program(program, start_addr=ADDR_MIN)

    cycles = cpu.run(max_cycles=10_000, trace=trace)

    print(f"\n─── Finished in {cycles} cycle(s) ───")
    cpu.state()

    final_r1 = cpu.registers.read("R1").to_int()
    print(f"R1 (counter) final value: {final_r1}  (expected 0)\n")
    assert final_r1 == 0, f"Countdown failed: R1 = {final_r1}"
    print("✓ Countdown completed successfully.")


if __name__ == "__main__":
    run_countdown(start=5, trace=True)
