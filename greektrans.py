# Greek character conversion utility

import unicodedata
from romanize import table

def from_reversed_table(table_rev):
    table = {}
    for key, value in table_rev.items():
        for letter in value:
            table[letter] = key
    return table

greek_letters = table["greekLetters"]
monotonic_table = from_reversed_table(table["monotonicTableRev"])
romanization_table = from_reversed_table(table["romanizationTableRev"])
romanization_table_ex = table["romanizationTableEx"]
greek_attrs_char = {chr(int(value, 16)): key for key, value in table["attributeCodes"].items()}

def is_letter(letter):
    return letter in table["greekLetters"]

def is_vowel(letter):
    return letter in table["greekVowels"]

def is_consonant(letter):
    return letter in table["greekConsonants"]

def strip(text):
    text = unicodedata.normalize("NFD", text)
    text = "".join(filter(lambda ch: ch not in greek_attrs_char, text))
    return unicodedata.normalize("NFC", text)

def string_map(map, text):
    return "".join([map[letter] if letter in map else letter for letter in text])

def monotonize(text):
    return string_map(monotonic_table, text)

def prepare_romanize(word):
    ret = ""
    if len(word) >= 1 and is_vowel(word[0]):
        if len(word) >= 2 and word[:2] in romanization_table_ex["combination"]:
            ret = word[:2]
            word = word[2:]
        else:
            ret = word[:1]
            word = word[1:]
    # check coronis: ex. κἀγώ = καὶ ἐγώ
    psili = table["attributes"]["PSILI"]
    for ch in word:
        ret += ch
        if ch in psili:
            ret += "'"
    return ret

def tokenize(text):
    token = ""
    type = 0
    for ch in text:
        t = 1 if ch in greek_letters else 2
        if type != t:
            if token:
                yield type, token
                token = ""
            type = t
        token += ch
    if token:
        yield type, token

def replaces(table, text):
    for key, value in table.items():
        text = text.replace(key, value)
    return text

def romanize(text, caron=True, dot_macron=True):
    ret = ""
    for type, token in tokenize(text):
        if type == 1:
            ret += prepare_romanize(token)
        else:
            ret += token
    ret = replaces(romanization_table_ex["combination"], ret)
    ret = "".join(map(lambda letter: romanization_table.get(letter, letter), ret))
    if caron:
        ret = replaces(romanization_table_ex["caron"], ret)
    if dot_macron:
        ret = replaces(romanization_table_ex["dotMacron"], ret)
    return ret

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
        print((monotonize if monotonic else romanize)(text).rstrip())
    except Exception as e:
        print(e)
        sys.exit(1)
