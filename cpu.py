from alu import add_ternary, subtract
from conversion import to_balanced_ternary


class CPU:

    def __init__(self, registers, memory):
        self.registers = registers
        self.memory = memory
        self.pc = 0


    def execute(self, instruction):

        op = instruction[0]

        if op == "MOV":

            reg = instruction[1]
            value = instruction[2]

            self.registers.write(reg, to_balanced_ternary(value))


        elif op == "ADD":

            r1 = instruction[1]
            r2 = instruction[2]

            a = self.registers.read(r1)
            b = self.registers.read(r2)

            result = add_ternary(a, b)

            self.registers.write(r1, result)


        elif op == "SUB":

            r1 = instruction[1]
            r2 = instruction[2]

            a = self.registers.read(r1)
            b = self.registers.read(r2)

            result = subtract(a, b)

            self.registers.write(r1, result)


        elif op == "LOAD":

            reg = instruction[1]
            addr = instruction[2]

            value = self.memory.read(addr)

            self.registers.write(reg, value)


        elif op == "STORE":

            reg = instruction[1]
            addr = instruction[2]

            value = self.registers.read(reg)

            self.memory.write(addr, value)


    def run(self, program):

        self.pc = 0

        while self.pc < len(program):

            instruction = program[self.pc]

            self.execute(instruction)

            self.pc += 1