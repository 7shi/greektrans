# Greek character conversion utility

import unicodedata
from romanize import table

def from_reversed_table(table_rev):
    table = {}
    for key, value in table_rev.items():
        for letter in value:
            table[letter] = key
    return table

romanization_table = from_reversed_table(table["romanizationTableRev"])
romanization_table_ex = table["romanizationTableEx"]
attribute_codes = {key: chr(int(value, 16)) for key, value in table["attributeCodes"].items()}

greek_attrs_char = {}
for key, value in attribute_codes.items():
    if key in ["TONOS", "OXIA", "PERISPOMENI"]:
        greek_attrs_char[value] = attribute_codes["TONOS"]
    elif key == "DIALYTIKA":
        greek_attrs_char[value] = attribute_codes["DIALYTIKA"]
    else:
        greek_attrs_char[value] = ""

def is_letter(letter):
    return letter in table["greekLetters"]

def is_vowel(letter):
    return letter in table["greekVowels"]

def is_consonant(letter):
    return letter in table["greekConsonants"]

def strip(text):
    text = unicodedata.normalize("NFD", text)
    for ch in greek_attrs_char:
        text = text.replace(ch, "")
    return unicodedata.normalize("NFC", text)

def replaces(table, text):
    for key, value in table.items():
        if key != value:
            text = text.replace(key, value)
    return text

def monotonize(text):
    text = unicodedata.normalize("NFD", text)
    text = replaces(greek_attrs_char, text)
    return unicodedata.normalize("NFC", text)

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
    text = unicodedata.normalize("NFC", text)
    token = ""
    type = 0
    for ch in text:
        t = 1 if is_letter(ch) else 2
        if type != t:
            if token:
                yield type, token
                token = ""
            type = t
        token += ch
    if token:
        yield type, token

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
