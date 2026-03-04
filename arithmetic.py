#Add Helper function to normalize numbers
def normalize(num):

    i = 0

    while i < len(num) - 1 and num[i] == 0:
        i += 1

    return num[i:]

def add_trit(a, b, carry=0):
    s = a + b + carry

    if s > 1:
        return s - 3, 1

    if s < -1:
        return s + 3, -1

    return s, 0

def add_ternary(a, b):
    
    # make both numbers same length
    max_len = max(len(a), len(b))
    
    a = [0]*(max_len - len(a)) + a
    b = [0]*(max_len - len(b)) + b

    result = []
    carry = 0

    # start from rightmost trit
    for i in range(max_len-1, -1, -1):
        
        digit, carry = add_trit(a[i], b[i], carry)
        result.insert(0, digit)

    if carry != 0:
        result.insert(0, carry)

    return normalize(result)