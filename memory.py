class Memory:

    def __init__(self, size=64):
        self.mem = [[0] for _ in range(size)]

    def write(self, address, value):
        self.mem[address] = value

    def read(self, address):
        return self.mem[address]

    def dump(self):
        return self.mem