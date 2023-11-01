import sys

if len(sys.argv) < 2:
    print(f"Usage: python {sys.argv[0]} <file>", file=sys.stderr)
    sys.exit(1)

text = ""
for f in sys.argv[1:]:
    with open(f, "r") as f:
        text += f.read()

chars = sorted(set(text))
for ch in chars:
    code = ord(ch)
    if code >= 128:
        print(f"{ch}\t{hex(code)}")
