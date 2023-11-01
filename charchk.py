import sys

if len(sys.argv) < 2:
    print(f"Usage: python {sys.argv[0]} <file>", file=sys.stderr)
    sys.exit(1)

text = ""
for f in sys.argv[1:]:
    with open(f, "r") as f:
        text += f.read()

# textに使われるすべての文字を拾ってソートする
chars = sorted(set(text))

# JavaScriptの連想配列として出力する
print("const greekChars = {")
for ch in chars:
    if ord(ch) >= 128:
        print(f'    "{ch}": "", // {hex(ord(ch))}')
print("};")
