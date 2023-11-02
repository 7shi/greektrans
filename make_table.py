# Create a table of Greek letters

import sys, os, re, json, unicodedata

class GreekChar:
    def __init__(self, code):
        self.code = code
        self.char = chr(code)
        self.nfd  = unicodedata.normalize("NFD", self.char)

        try:
            self.name = unicodedata.name(self.char)
        except ValueError:
            self.name = ""

        if m := re.match(r"GREEK (CAPITAL|SMALL) (LETTER [A-Z]+)", self.name):
            self.capital = m.group(1) == "CAPITAL"
            self.greek_name = m.group(2)
        else:
            self.capital = False
            self.greek_name = ""

        self.attrs = set()
        if m := re.match(r"(.*) WITH (.*)", self.name):
            self.base_name = m.group(1)
            for attr in m.group(2).split(" AND "):
                self.attrs.add(attr)
        else:
            self.base_name = self.name

        self.tonos          = "TONOS"          in self.attrs # acute (modern)
        self.dialytika      = "DIALYTIKA"      in self.attrs # diaeresis (tréma)
        self.oxia           = "OXIA"           in self.attrs # acute (ancient)
        self.perispomeni    = "PERISPOMENI"    in self.attrs # circumflex
        self.varia          = "VARIA"          in self.attrs # grave
        self.psili          = "PSILI"          in self.attrs # smooth breathing
        self.dasia          = "DASIA"          in self.attrs # rough breathing (aspirated)
        self.prosgegrammeni = "PROSGEGRAMMENI" in self.attrs # iota subscript (capital)
        self.ypogegrammeni  = "YPOGEGRAMMENI"  in self.attrs # iota subscript (small)
        self.macron         = "MACRON"         in self.attrs # macron
        self.vrachy         = "VRACHY"         in self.attrs # breve

    def __str__(self):
        return f"{self.char}[U+{self.code:04x}]: {self.name}"
    
    def json(self):
        return {
            "code": f"{self.code:04x}",
            "nfd": " ".join([f"{ord(ch):04x}" for ch in self.nfd]),
            "name": self.name,
        }

# Read Unicode names for Greek
greek_letters_info = {}
for s, e in [(0x384, 0x3d0), (0x1f00, 0x2000)]:
    for code in range(s, e):
        gch = GreekChar(code)
        if gch.greek_name:
            greek_letters_info[gch.char] = gch

# extract: GREEK CAPITAL/SMALL LETTER
greek_capital_letters = "".join([gch.char for gch in greek_letters_info.values() if gch.capital])
greek_small_letters = "".join([gch.char for gch in greek_letters_info.values() if not gch.capital])
greek_letters = greek_capital_letters + greek_small_letters
greek_letters_rev = {gch.name: gch.char for gch in greek_letters_info.values()}

attrs = { "": "" } # ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρςστυφχψω
for gch in greek_letters_info.values():
    if len(gch.attrs) == 0:
        attrs[""] += gch.char
    else:
        for attr in gch.attrs:
            if attr not in attrs:
                attrs[attr] = ""
            attrs[attr] += gch.char

def strip1(letter):
    gch = greek_letters_info.get(letter)
    return gch.nfd[0] if gch else letter

def monotonize1(letter):
    gch = greek_letters_info.get(letter)
    if not gch:
        return letter
    tonos = gch.tonos or gch.perispomeni or gch.oxia
    if tonos and gch.dialytika:
        ret = greek_letters_rev.get(gch.base_name + " WITH DIALYTIKA AND TONOS")
        if ret: return ret
    if gch.dialytika:
        return greek_letters_rev[gch.base_name + " WITH DIALYTIKA"]
    elif tonos:
        return greek_letters_rev[gch.base_name + " WITH TONOS"]
    else:
        return gch.nfd[0]

strip_table = {key: key2 for key in greek_letters if key != (key2 := strip1(key))}
monotonic_table = {key: key2 for key in greek_letters if key != (key2 := monotonize1(key))}

def is_letter(letter):
    return letter in greek_letters

def is_vowel(letter):
    return strip1(letter) in "ΑΕΗΙΟΥΩαεηιουω"

def is_consonant(letter):
    return is_letter(letter) and not is_vowel(letter)

greek_vowels = "".join(filter(is_vowel, greek_letters))
greek_consonants = "".join(filter(is_consonant, greek_letters))

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
    "unicodeData": {key: gch.json() for key, gch in greek_letters_info.items()},
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

class TestGreekTrans(unittest.TestCase):
    def test(self):
        self.assertEqual(prepare_romanize("κἀγώ"), "κἀ'γώ")
        self.assertEqual(romanize("Ἐγὼ δ' εἰς τὴν ἀγρίαν ὁδὸν εἰσῆλθον."),
                         "Egṑ d' eis tḕn agrían hodòn eisêlthon.")

    def tearDown(self):
        # The Lord's Prayer
        # https://en.wikipedia.org/wiki/Greek_diacritics#Examples

        with open("lords_prayer.txt", "r", encoding="utf-8") as file:
            sample = file.read()

        # Note: The results do not match because of removing without grammar.
        print(monotonize(sample))

        print(romanize(sample))
        # print(romanize(to_monotonic(sample)))

unittest.main()
