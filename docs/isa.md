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
-  =  −1   (also accepted: _ N n)
0  =   0   (also accepted: z Z)
+  =  +1   (also accepted: 1 p P)
```

Example ternary number (value = 8):

```
+ 0 -
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

The CPU contains **9 general-purpose registers** plus two special registers.

```
R0  R1  R2  R3  R4  R5  R6  R7  R8
```

> **R0 is the zero register.** Reads always return 0; writes are silently ignored.
> Use R0 as a `null` operand or to cheaply load zero into another register.

Special registers (not directly addressable):

| Register | Purpose |
|----------|---------|
| PC | Program Counter — address of the next instruction |
| FLAGS | Condition flags: `sign` (trit 0), `carry` (trit 1), `zero` (trit 2) |

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

| Opcode | Mnemonic | Description |
|-------:|----------|-------------|
|      0 | NOP      | no operation |
|      1 | MOV      | RA ← immediate |
|      2 | ADD      | RA ← RA + RB |
|      3 | SUB      | RA ← RA − RB |
|      4 | NEG      | RA ← −RA |
|      5 | LOAD     | RA ← MEM[RB + imm] |
|      6 | STORE    | MEM[RA + imm] ← RB |
|      7 | JMP      | PC ← imm |
|      8 | JZ       | if FLAGS.zero: PC ← imm |
|      9 | JNZ      | if not FLAGS.zero: PC ← imm |
|     10 | TAND     | RA ← RA AND RB  (tritwise) |
|     11 | TOR      | RA ← RA OR RB   (tritwise) |
|     12 | TMUL     | RA ← RA × RB    (tritwise Galois, no carry) |
|     13 | MUL      | RA ← RA × RB    (full arithmetic multiply) |
|    −13 | HALT     | stop execution |

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
LOAD Ra Rb imm
```

Loads memory value at address `Rb + imm` into register `Ra`.

```
Ra = MEM[Rb + imm]
```

---

## STORE

```
STORE Ra Rb imm
```

Stores register `Rb` to memory at address `Ra + imm`.

```
MEM[Ra + imm] = Rb
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

## TAND

```
TAND Ra Rb
```

Trit-wise AND (min) of `Ra` and `Rb`, result stored in `Ra`.

```
Ra = Ra AND Rb   (per-trit)
```

---

## TOR

```
TOR Ra Rb
```

Trit-wise OR (max) of `Ra` and `Rb`, result stored in `Ra`.

```
Ra = Ra OR Rb    (per-trit)
```

---

## TMUL

```
TMUL Ra Rb
```

Trit-wise Galois-field multiply (no carry), result stored in `Ra`.

```
Ra = Ra * Rb     (per-trit, mod 3)
```

---

## MUL

```
MUL Ra Rb
```

Full arithmetic multiply. Result is the lower 9 trits stored in `Ra`.

```
Ra = Ra × Rb
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

- assembler for `.asm` / `.tas` files
- stack instructions (`PUSH`, `POP`)
- function call / return (`CALL`, `RET`)
- interrupts and exception handling
- memory segmentation
- floating-point or extended-precision trits

---

# Project Status

This ISA is part of an experimental balanced ternary CPU simulator.

The current implementation focuses on clarity and experimentation rather than performance.

The architecture may evolve as the project develops.
