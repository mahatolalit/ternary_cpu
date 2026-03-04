# Ternary CPU Execution Model

## Overview

This document describes how the ternary CPU executes instructions defined in the ISA.

The CPU follows a simple execution cycle similar to classic RISC processors.

Execution consists of three stages:

```

Fetch → Decode → Execute

```

---

# CPU Components

The CPU consists of the following major components:

- **Program Counter (PC)** — address of the next instruction
- **Register File** — R0–R8 general purpose + FLAGS
  - R0 is the *zero register*: always reads 0, writes are ignored
  - FLAGS stores the result of the last operation: `sign` (trit 0), `carry` (trit 1), `zero` (trit 2)
- **Arithmetic Logic Unit (ALU)** — arithmetic, logical, and tritwise operations
- **Memory Interface** — 729-cell balanced-ternary address space (addresses −364…+364)

---

# Program Counter

The Program Counter (PC) stores the address of the next instruction.

Since each instruction is **2 words (18 trits)**:

```

instruction_word_1 = memory[PC]
instruction_word_2 = memory[PC + 1]

```

After fetching:

```

PC = PC + 2

```

unless modified by a jump instruction.

---

# Fetch Stage

The CPU fetches an instruction from memory.

```

word0 = memory[PC]
word1 = memory[PC + 1]
instruction = combine(word0, word1)

```

---

# Decode Stage

The instruction is divided into fields:

```

| opcode | RA | RB | flags | immediate |
| 3t     |2t  |2t  |2t     | 9t        |

```

The opcode determines which operation to execute.

---

# Execute Stage

The CPU executes the instruction depending on the opcode.

### Arithmetic

```
ADD Ra Rb    →  Ra = Ra + Rb
SUB Ra Rb    →  Ra = Ra - Rb
NEG Ra       →  Ra = -Ra
MUL Ra Rb    →  Ra = Ra × Rb  (lower 9 trits)
```

### Tritwise Logic

```
TAND Ra Rb   →  Ra = Ra AND Rb  (per-trit min)
TOR  Ra Rb   →  Ra = Ra OR  Rb  (per-trit max)
TMUL Ra Rb   →  Ra = Ra ×  Rb  (per-trit Galois mod 3)
```

### Data Movement

```
MOV  Ra imm        →  Ra = imm
LOAD Ra Rb imm     →  Ra = MEM[Rb + imm]
STORE Ra Rb imm    →  MEM[Ra + imm] = Rb
```

### Control Flow

```
JMP  imm         →  PC = imm
JZ   Ra imm      →  if FLAGS.zero:  PC = imm
JNZ  Ra imm      →  if !FLAGS.zero: PC = imm
```

Every instruction updates FLAGS (sign, carry, zero) based on the result.

---

# CPU Execution Loop

The CPU repeatedly performs the execution cycle until a HALT instruction is encountered.

Pseudo-code:

```

while running:

```
instruction = fetch()

decoded = decode(instruction)

execute(decoded)
```

```

---

# HALT Instruction

The `HALT` instruction stops CPU execution.

```

running = False

```

---

# Future Extensions

Possible future improvements:

- pipeline stages
- stack support (`PUSH` / `POP`)
- interrupts and exception handling
- assembler for text-format programs
- floating-point trit encoding

---