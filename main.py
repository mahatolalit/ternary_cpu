from trit import *
from conversion import *
from arithmetic import *
from alu import *
from registers import *
from memory import *
from cpu import *


print("Testing trits:")
print(is_trit(-1))
print(is_trit(0))
print(is_trit(1))
print(is_trit(2))


print("\nSymbol conversion:")
print(trit_to_symbol(1))
print(trit_to_symbol(-1))
print(symbol_to_trit("+"))


print("\nExample ternary number:")
num = [1, -1, 0, 1]
print(print_ternary(num))


print("\nDecimal → Balanced Ternary")

num = 19
tern = to_balanced_ternary(num)

print("Decimal:", num)
print("Ternary:", print_ternary(tern))


print("\nBalanced Ternary → Decimal")

value = from_balanced_ternary(tern)

print("Back to decimal:", value)


print("\nTesting Trit Addition")

tests = [
    (1, 1, 0),
    (-1, -1, 0),
    (1, -1, 0),
]

for a, b, c in tests:
    result, carry = add_trit(a, b, c)
    print(a, "+", b, "=", result, "carry:", carry)


#Testing Multi-Trit Addition
print("\nTesting Multi-Trit Addition")

a = [1, -1, 0, 1]     # + - 0 +
b = [1, 1, -1, 0]     # + + - 0

result = add_ternary(a, b)

print("A:", print_ternary(a))
print("B:", print_ternary(b))
print("Result:", print_ternary(result))


#Testing ALU Operations
print("\nTesting ALU")

a = to_balanced_ternary(19)
b = to_balanced_ternary(7)

print("A:", print_ternary(a))
print("B:", print_ternary(b))

print("\nADD:")
print(print_ternary(add_ternary(a,b)))

print("\nSUB:")
print(print_ternary(subtract(a,b)))

print("\nNEG A:")
print(print_ternary(negate(a)))


#Testing Registers
print("\nTesting Registers")

regs = Registers()

regs.write("R0", to_balanced_ternary(19))
regs.write("R1", to_balanced_ternary(7))

print("R0:", print_ternary(regs.read("R0")))
print("R1:", print_ternary(regs.read("R1")))


#Testing Memory
print("\nTesting Memory")

mem = Memory()

mem.write(0, to_balanced_ternary(19))
mem.write(1, to_balanced_ternary(7))

print("Mem[0]:", print_ternary(mem.read(0)))
print("Mem[1]:", print_ternary(mem.read(1)))

#Testing CPU
print("\nTesting CPU")

regs = Registers()
mem = Memory()

cpu = CPU(regs, mem)

program = [

    ("MOV", "R0", 19),
    ("MOV", "R1", 7),

    ("ADD", "R0", "R1"),

    ("STORE", "R0", 0),

]

cpu.run(program)

print("R0:", print_ternary(regs.read("R0")))
print("Memory[0]:", print_ternary(mem.read(0)))


#Testing Loop Program
print("\nTesting Loop Program")

regs = Registers()
mem = Memory()
cpu = CPU(regs, mem)

program = [

    ("MOV", "R0", 5),
    ("MOV", "R1", 1),

    ("SUB", "R0", "R1"),
    ("JNZ", "R0", 2),

]

cpu.run(program)

print("Final R0:", print_ternary(regs.read("R0")))