TRITS = [-1, 0, 1]

def is_trit(x):
    return x in TRITS


def trit_to_symbol(t):
    mapping = {
        1: "+",
        0: "0",
        -1: "-"
    }
    return mapping[t]


def symbol_to_trit(s):
    mapping = {
        "+": 1,
        "0": 0,
        "-": -1
    }
    return mapping[s]


def print_ternary(num):
    return " ".join(trit_to_symbol(t) for t in num)