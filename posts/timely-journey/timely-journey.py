import string

ALPHA = string.ascii_uppercase
A2I = {c: i for i, c in enumerate(ALPHA)}

def parse_keys(d: str):
    keys = []
    i = 0
    while i < len(d):
        ch = d[i]
        if ch.isdigit():
            keys.append(int(ch))
            i += 1
        elif ch == '[':
            j = d.find(']', i + 1)
            if j == -1:
                raise ValueError("Unclosed '[' in digits string")
            token = d[i + 1 : j]
            if not token.isdigit():
                raise ValueError(f"Non-numeric token in brackets: [{token}]")
            keys.append(int(token))
            i = j + 1
        else:
            i += 1
    return keys

def caesar_with_keys(letters: str, keys, direction: str = "right") -> str:
    letters = "".join(ch for ch in letters.upper() if ch.isalpha())
    if len(letters) != len(keys):
        raise ValueError(f"Length mismatch: letters={len(letters)} keys={len(keys)}")

    out = []
    for c, k in zip(letters, keys):
        k %= 26
        if direction == "right":
            out.append(ALPHA[(A2I[c] + k) % 26])
        elif direction == "left":
            out.append(ALPHA[(A2I[c] - k) % 26])
        else:
            raise ValueError("direction must be 'right' or 'left'")
    return "".join(out)

B_letters = "REARKYBKAPNBLIAIADGLRDNZ"
B_digits  = "5302762144636[10]0949271507"
B_keys = parse_keys(B_digits)

print("B right:", caesar_with_keys(B_letters, B_keys, "right"))
print("B left: ", caesar_with_keys(B_letters, B_keys, "left"))

R_letters = "ASCAAAEGHJIIKEGMNOSUMVRS"
R_digits  = "090345211023298333009166"
R_keys = parse_keys(R_digits)

print("R right:", caesar_with_keys(R_letters, R_keys, "right"))
print("R left: ", caesar_with_keys(R_letters, R_keys, "left"))
