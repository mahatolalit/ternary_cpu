# Ternary CPU

A balanced-ternary 9-trit CPU emulator written in Python.

## Documentation

| Doc | Contents |
|-----|----------|
| [docs/isa.md](docs/isa.md) | Full ISA — number system, word size, registers, instruction format, opcode table, examples |
| [docs/cpu_design.md](docs/cpu_design.md) | CPU execution model — fetch/decode/execute stages, pipeline, halt behaviour |

## Architecture

| Property          | Value                               |
|-------------------|-------------------------------------|
| Number system     | Balanced ternary (trits: −1, 0, +1) |
| Word size         | 9 trits (values −9841 … +9841)      |
| Instruction width | 18 trits (2 memory words)           |
| Registers         | R0–R8 (GP) + PC + FLAGS             |
| Memory            | 729 cells (3⁶), addresses −364…+364 |
| Architecture      | RISC-style, fixed instruction width |

→ Full execution model: [docs/cpu_design.md](docs/cpu_design.md)

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

This CPU implements 15 opcodes. For the full opcode table, instruction
format, register encoding, and usage examples see
[docs/isa.md](docs/isa.md).

**Quick reference:**

| Group | Mnemonics |
|-------|-----------|
| Data movement | `MOV`, `LOAD`, `STORE` |
| Arithmetic | `ADD`, `SUB`, `NEG`, `MUL` |
| Tritwise logic | `TAND`, `TOR`, `TMUL` |
| Control flow | `JMP`, `JZ`, `JNZ`, `HALT`, `NOP` |

→ Full opcode table and encoding: [docs/isa.md](docs/isa.md)

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
