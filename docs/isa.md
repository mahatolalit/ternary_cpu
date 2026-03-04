# Ternary CPU Instruction Set Architecture (ISA)

## Overview

This document defines the Instruction Set Architecture (ISA) for the experimental balanced ternary CPU used in this project.

The goal of this architecture is to explore the design of a **balanced ternary processor** while maintaining principles similar to modern RISC architectures such as RISC-V.

The architecture is intentionally small and simple, but structured so it can evolve into a more complete CPU design.

Key design goals:

- Balanced ternary number system
- Simple RISC-style instruction set
- Fixed instruction width
- Register-based computation
- Easy extensibility for experimentation

---

# Number System

This CPU uses **balanced ternary digits (trits)**.

A trit has three possible values:

```

-1
0
+1

```

Symbol representation used in this project:

```

* = -1
  0  =  0

- = +1

```

Example ternary number:

```

* * 0 +

```

---

# Architecture Summary

| Property | Value |
|--------|--------|
| Number system | Balanced ternary |
| Word size | 9 trits |
| Instruction width | 18 trits |
| Registers | 9 general purpose |
| Memory size | 729 cells |
| Architecture style | RISC |

---

# Word Size

A **word** is the fundamental data unit of the CPU.

```

1 word = 9 trits

```

Possible values:

```

-9841 → +9841

```

since:

```

3⁹ = 19683 possible values

```

---

# Registers

The CPU contains **9 general-purpose registers**.

```

R0
R1
R2
R3
R4
R5
R6
R7
R8

```

Each register stores:

```

1 word (9 trits)

```

Registers are used for:

- arithmetic operations
- temporary values
- memory addressing

Most instructions operate directly on registers.

---

# Memory Model

The system memory consists of:

```

729 memory cells

```

Since:

```

3⁶ = 729

```

Each memory cell stores:

```

1 word (9 trits)

```

Memory can contain:

- program instructions
- data values
- stack memory

---

# Instruction Width

All instructions are **18 trits wide**.

```

1 instruction = 2 words

```

This allows instructions to include:

- opcode
- register operands
- memory addresses
- immediate values

---

# Instruction Format

The general instruction layout:

```

| Opcode | RegA | RegB | Flags | Immediate / Address |
| 3 trit | 2 tr | 2 tr | 2 tr  |        9 trits       |

```

Explanation:

| Field | Size | Description |
|------|------|-------------|
| Opcode | 3 trits | operation identifier |
| RegA | 2 trits | register operand |
| RegB | 2 trits | second register |
| Flags | 2 trits | instruction modifiers |
| Immediate | 9 trits | value or memory address |

---

# Opcode Table

| Opcode | Instruction | Description |
|------|-------------|-------------|
| 0 | NOP | no operation |
| 1 | MOV | move immediate to register |
| 2 | ADD | register addition |
| 3 | SUB | register subtraction |
| 4 | NEG | negate register |
| 5 | LOAD | load memory into register |
| 6 | STORE | store register to memory |
| 7 | JMP | unconditional jump |
| 8 | JZ | jump if register is zero |
| 9 | JNZ | jump if register not zero |
| 10 | HALT | stop execution |

Remaining opcodes are reserved for future expansion.

---

# Instruction Descriptions

## NOP

```

NOP

```

Performs no operation.

Used for timing alignment or placeholders.

---

## MOV

```

MOV Rn, immediate

```

Moves an immediate value into a register.

Example:

```

MOV R0 5

```

---

## ADD

```

ADD Ra Rb

```

Adds register `Rb` to register `Ra`.

```

Ra = Ra + Rb

```

Example:

```

ADD R1 R2

```

---

## SUB

```

SUB Ra Rb

```

Subtracts `Rb` from `Ra`.

```

Ra = Ra - Rb

```

---

## NEG

```

NEG Ra

```

Negates the value in the register.

```

Ra = -Ra

```

---

## LOAD

```

LOAD Ra address

```

Loads memory value into register.

```

Ra = MEM[address]

```

---

## STORE

```

STORE Ra address

```

Stores register value into memory.

```

MEM[address] = Ra

```

---

## JMP

```

JMP address

```

Unconditional jump.

```

PC = address

```

---

## JZ

```

JZ Ra address

```

Jump if register value is zero.

```

if Ra == 0
PC = address

```

---

## JNZ

```

JNZ Ra address

```

Jump if register is not zero.

```

if Ra != 0
PC = address

```

---

## HALT

```

HALT

```

Stops CPU execution.

---

# Example Program

Example program that counts down from 5:

```

MOV R0 5
MOV R1 1

LOOP
SUB R0 R1
JNZ R0 LOOP

HALT

```

Execution:

```

5 → 4 → 3 → 2 → 1 → 0

```

---

# Future Extensions

Possible future features:

- ternary machine code encoding
- assembler for `.asm` files
- stack instructions
- function calls
- interrupts
- memory segmentation

---

# Project Status

This ISA is part of an experimental balanced ternary CPU simulator.

The current implementation focuses on clarity and experimentation rather than performance.

The architecture may evolve as the project develops.
