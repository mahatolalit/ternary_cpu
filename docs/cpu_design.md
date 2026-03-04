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

- Program Counter (PC)
- Register File
- Arithmetic Logic Unit (ALU)
- Memory Interface

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

Example operations:

### Arithmetic

```

ADD Ra Rb
Ra = Ra + Rb

```

### Memory

```

LOAD Ra addr
Ra = memory[addr]

```
```

STORE Ra addr
memory[addr] = Ra

```

### Control Flow

```

JMP addr
PC = addr

```
```

JNZ Ra addr
if Ra != 0:
PC = addr

```

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
- stack support
- interrupts
- assembler
- machine code encoding

---