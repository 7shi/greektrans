# Create a table of Greek letters

import sys, os, re, json

# Download if it does not exist
if not os.path.exists("greek.txt"):
    import urllib.request
    urllib.request.urlretrieve("https://www.w3.org/International/Spread/greek.txt", "greek.txt")

with open("greek.txt", "r", encoding="utf-8") as file:
    greek_data_entity = file.read()

# Read greek_data_entity line by line and convert it into a JavaScript associative array
letters = {}
for line in greek_data_entity.splitlines():
    m = re.search(r'U([0-9A-F]{4}) SDATA "\[(.*)\]"', line)
    if m:
        code = m.group(1)
        char = chr(int(code, 16))
        sdata = m.group(2)
        letters[char] = sdata

class Assoc:
    @staticmethod
    def swap(assoc):
        return {value: key for key, value in assoc.items()}

    @staticmethod
    def filter(predicate, assoc):
        return {key: value for key, value in assoc.items() if predicate(key, value)}

# TONOS/OXIA: acute, DIALYTIKA: diaeresis (tréma), PERISPOMENI: circumflex
# 'Ι': 'GREEK CAPITAL LETTER IOTA'
# 'ι': 'GREEK SMALL LETTER IOTA'
# 'ί': 'GREEK SMALL LETTER IOTA WITH TONOS'
# 'ϊ': 'GREEK SMALL LETTER IOTA WITH DIALYTIKA'
# 'ΐ': 'GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS'
# 'ῖ': 'GREEK SMALL LETTER IOTA WITH PERISPOMENI'
# 'ῗ': 'GREEK SMALL LETTER IOTA WITH DIALYTIKA AND PERISPOMENI'

# extract: GREEK CAPITAL/SMALL LETTER
greek_capital_letters = "".join(Assoc.filter(lambda _, value: bool(re.search(r'GREEK CAPITAL LETTER', value)), letters).keys())
greek_small_letters = "".join(Assoc.filter(lambda _, value: bool(re.search(r'GREEK SMALL LETTER', value)), letters).keys())
greek_letters = greek_capital_letters + greek_small_letters
greek_letters_info = {key: letters[key] for key in greek_letters}
greek_letters_rev = Assoc.swap(greek_letters_info)

# "": ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρςστυφχψω
# TONOS, DIALYTIKA, OXIA, PERISPOMENI, VARIA: grave,
# PSILI: smooth breathing, DASIA: rough breathing (aspirated),
# PROSGEGRAMMENI: capital iota subscript, YPOGEGRAMMENI: small iota subscript,
# VRACHY: breve, MACRON
attrs = { "": "" }
for key, value in greek_letters_info.items():
    # WITH以下を取得
    m = re.search(r" WITH (.*)", value)
    if m:
        # ANDで分割
        for attr in m.group(1).split(" AND "):
            if attr not in attrs:
                attrs[attr] = ""
            attrs[attr] += key
    else:
        attrs[""] += key

def strip1(letter):
    sdata = letters.get(letter)
    if not sdata:
        return letter
    name = re.sub(r" WITH .*", "", sdata)
    return greek_letters_rev.get(name, letter)

# extract: WITH DIALYTIKA
dialytika_letters = Assoc.swap(Assoc.filter(lambda _, value: bool(re.search(r'WITH DIALYTIKA$', value)), greek_letters_info))

# extract: WITH TONOS
tonos_letters = Assoc.swap(Assoc.filter(lambda _, value: bool(re.search(r'WITH TONOS$', value)), greek_letters_info))

# extract: WITH DIAYTIKA AND TONOS
dialytika_tonos_letters = Assoc.swap(Assoc.filter(lambda _, value: bool(re.search(r'WITH DIALYTIKA AND TONOS$', value)), greek_letters_info))

def monotonize1(letter):
    sdata = letters.get(letter)
    if not sdata:
        return letter
    name = re.sub(r" WITH .*", "", sdata)
    basic = greek_letters_rev.get(name)
    if not basic:
        return letter
    dialytika = bool(re.search(r"DIALYTIKA", sdata))
    tonos = bool(re.search(r"TONOS|PERISPOMENI|OXIA", sdata))
    if tonos and dialytika:
        ret = dialytika_tonos_letters.get(name + " WITH DIALYTIKA AND TONOS")
        if ret: return ret
    if dialytika:
        return dialytika_letters.get(name + " WITH DIALYTIKA")
    elif tonos:
        return tonos_letters.get(name + " WITH TONOS")
    else:
        return basic

strip_table = {key: key2 for key in letters.keys() if key != (key2 := strip1(key))}
monotonic_table = {key: key2 for key in letters.keys() if key != (key2 := monotonize1(key))}

def is_letter(letter):
    return letter in greek_letters_info

def is_vowel(letter):
    return strip1(letter) in "ΑΕΗΙΟΥΩαεηιουω"

def is_consonant(letter):
    return is_letter(letter) and not is_vowel(letter)

greek_vowels = "".join(Assoc.filter(lambda key, _: is_vowel(key), greek_letters_info).keys())
greek_consonants = "".join(Assoc.filter(lambda key, _: is_consonant(key), greek_letters_info).keys())

# Create romanization table template
table_name = "romanize"
if not os.path.exists(f"{table_name}-letter.json"):
    with open(f"{table_name}-letter.json", "w", encoding="utf-8") as file:
        json.dump({letter: "" for letter in greek_letters}, file, ensure_ascii=False, indent=2)
    print(f"Please edit `{table_name}-letter.json`.", file=sys.stderr)
    sys.exit(1)

with open(f"{table_name}-letter.json", "r", encoding="utf-8") as file:
    romanization_table = json.load(file)

with open(f"{table_name}-extra.json", "r", encoding="utf-8") as file:
    romanization_table_ex = json.load(file)

def reverse_table(table):
    rev = {}
    for key, value in table.items():
        if value not in rev:
            rev[value] = ""
        rev[value] += key
    return rev

# convert to JSON
table = json.dumps({
    "letters": letters,
    "greekLetters": greek_letters,
    "greekCapitalLetters": greek_capital_letters,
    "greekSmallLetters": greek_small_letters,
    "attributes": attrs,
    "greekVowels": greek_vowels,
    "greekConsonants": greek_consonants,
    "stripTableRev": reverse_table(strip_table),
    "monotonicTableRev": reverse_table(monotonic_table),
    "romanizationTableRev": reverse_table(romanization_table),
    "romanizationTableEx": romanization_table_ex,
}, ensure_ascii=False, indent=2)

# Save to file
with open(f"{table_name}.json", "w", encoding="utf-8") as file:
    file.write(table)

# Generate JavaScript module
with open(f"{table_name}.js", "w", encoding="utf-8") as file:
    file.write(f"export const table = {table};");

# Generate Python module
with open(f"{table_name}.py", "w", encoding="utf-8") as file:
    file.write(f"table = {table}");

### Additional Impementation

def strip(text):
    return "".join(map(strip1, text))

def monotonize(text):
    return "".join(map(monotonize1, text))

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
    psili = attrs["PSILI"]
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

### unit test

import unittest
test = unittest.TestCase()
test.assertEqual(prepare_romanize("κἀγώ"), "κἀ'γώ")
test.assertEqual(romanize("Ἐγὼ δ' εἰς τὴν ἀγρίαν ὁδὸν εἰσῆλθον."),
                 "Egṑ d' eis tḕn agrían hodòn eisêlthon.")

### Sample

# The Lord's Prayer
# https://en.wikipedia.org/wiki/Greek_diacritics#Examples

with open("lords_prayer.txt", "r", encoding="utf-8") as file:
    sample = file.read()

# Note: The results do not match because of removing without grammar.
print(monotonize(sample))

print(romanize(sample))
# print(romanize(to_monotonic(sample)))
