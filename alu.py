from arithmetic import add_ternary


def negate(a):
    return [-x for x in a]


def subtract(a, b):
    neg_b = negate(b)
    return add_ternary(a, neg_b)


def compare(a, b):

    if a == b:
        return 0

    if len(a) > len(b):
        return 1

    if len(a) < len(b):
        return -1

    for x, y in zip(a, b):
        if x > y:
            return 1
        if x < y:
            return -1

    return 0