# Greek character conversion utility

from romanize import table

def from_reverse_table(table_rev):
    table = {}
    for key, value in table_rev.items():
        for letter in value:
            table[letter] = key
    return table

strip_table = from_reverse_table(table["stripTableRev"])
monotonic_table = from_reverse_table(table["monotonicTableRev"])
romanization_table = from_reverse_table(table["romanizationTableRev"])

def is_letter(letter):
    return letter in table["greekLetters"]

def is_vowel(letter):
    return letter in table["greekVowels"]

def is_consonant(letter):
    return letter in table["greekConsonants"]

def string_map(map, text):
    return "".join([map[letter] if letter in map else letter for letter in text])

def strip(text):
    return string_map(strip_table, text)

def to_monotonic(text):
    return string_map(monotonic_table, text)

def replaces(table, text):
    for key, value in table.items():
        text = text.replace(key, value)
    return text

def romanize(text, caron=True, ogonek_macron=True):
    text = replaces(table["romanizationTableEx"]["combination"], text)
    text = string_map(romanization_table, text)
    if caron:
        text = replaces(table["romanizationTableEx"]["caron"], text)
    if ogonek_macron:
        text = replaces(table["romanizationTableEx"]["ogonekMacron"], text)
    return text

if __name__ == "__main__":
    import sys
    file, monotonic = None, False
    if len(sys.argv) > 1:
        if sys.argv[1] == "-m":
            monotonic = True
            file = sys.argv[2]
        else:
            file = sys.argv[1]
    if not file:
        print("usage: python el-utils.py [-m] input_file", file=sys.stderr)
        sys.exit(1)
    try:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
        print((to_monotonic if monotonic else romanize)(text).rstrip())
    except Exception as e:
        print(e)
        sys.exit(1)
