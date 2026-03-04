class Registers:

    def __init__(self):
        self.reg = {
            "R0": [0],
            "R1": [0],
            "R2": [0],
            "R3": [0],
        }

    def write(self, name, value):
        self.reg[name] = value

    def read(self, name):
        return self.reg[name]

    def dump(self):
        return self.reg