# Ternary CPU

A balanced-ternary 9-trit CPU emulator written in Python.

## Architecture

| Property         | Value                            |
|------------------|----------------------------------|
| Number system    | Balanced ternary (trits: −1, 0, +1) |
| Word size        | 9 trits (values −9841 … +9841)   |
| Instruction width | 18 trits (2 memory words)       |
| Registers        | R0–R8 (GP) + PC + FLAGS          |
| Memory           | 729 cells (3⁶), addresses −364…+364 |
| Architecture     | RISC-style, fixed instruction width |

## Directory Structure

```
ternary_cpu/
│
├── docs/
│   ├── isa.md           ISA specification
│   └── cpu_design.md    CPU execution model
│
├── cpu/
│   ├── __init__.py
│   ├── trits.py         Trit primitives, gates, Word type
│   ├── ternary.py       Balanced-ternary arithmetic
│   ├── alu.py           ALU operations and flags
│   ├── registers.py     Register file (R0–R8, PC, FLAGS)
│   ├── memory.py        729-cell memory
│   └── cpu.py           Fetch/decode/execute CPU, instruction encoding
│
├── examples/
│   └── countdown.py     Demo: count down from 5 to 0
│
├── main.py              Unit tests and integration demo
├── README.md
└── requirements.txt
```

## Instruction Set

| Opcode | Mnemonic | Operation                       |
|-------:|----------|----------------------------------|
|      0 | NOP      | No operation                    |
|      1 | MOV      | RA ← immediate                  |
|      2 | ADD      | RA ← RA + RB                    |
|      3 | SUB      | RA ← RA − RB                    |
|      4 | NEG      | RA ← −RA                        |
|      5 | LOAD     | RA ← MEM[RB + imm]              |
|      6 | STORE    | MEM[RA + imm] ← RB              |
|      7 | JMP      | PC ← imm                        |
|      8 | JZ       | if zero: PC ← imm               |
|      9 | JNZ      | if not zero: PC ← imm           |
|     10 | TAND     | RA ← RA AND RB (tritwise)       |
|     11 | TOR      | RA ← RA OR  RB (tritwise)       |
|     12 | TMUL     | RA ← RA * RB   (tritwise Galois)|
|     13 | MUL      | RA ← RA × RB   (arithmetic)     |
|    −13 | HALT     | Stop execution                   |

## Instruction Format (18 trits)

```
memory[PC]     =  [ op2 op1 op0 | ra1 ra0 | rb1 rb0 | fl1 fl0 ]
                   ─── opcode     ── RA ──   ── RB ──   flags
memory[PC + 1] =  [ imm8 imm7 … imm0 ]
```

## Quick Start

```python
from cpu.cpu    import CPU, encode_instruction, Opcode
from cpu.memory import ADDR_MIN

cpu = CPU()

# Build: MOV R1, 42 / HALT
program = []
h, l = encode_instruction(Opcode.MOV, ra="R1", imm=42)
program += [h, l]
h, l = encode_instruction(Opcode.HALT)
program += [h, l]

cpu.load_program(program, start_addr=ADDR_MIN)
cpu.run()
cpu.state()
print(cpu.registers.read("R1").to_int())  # → 42
```

Run the countdown demo:

```bash
python examples/countdown.py
```

Run all tests:

```bash
python main.py
```

## Requirements

Python 3.10+, no external dependencies.
