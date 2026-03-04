def to_balanced_ternary(n):
    digits = []

    while n != 0:
        r = n % 3
        n //= 3

        if r == 2:
            r = -1
            n += 1

        digits.append(r)

    return digits[::-1] or [0]


def from_balanced_ternary(digits):
    value = 0

    for d in digits:
        value = value * 3 + d

    return value