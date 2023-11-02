# Create a table of Greek letters

import sys, os, re, json, unicodedata

class UnicodeChar:
    def __init__(self, code):
        self.code = code
        self.char = chr(code)
        self.nfd  = unicodedata.normalize("NFD", self.char)

        try:
            self.name = unicodedata.name(self.char)
        except ValueError:
            self.name = ""

        if m := re.match(r"([A-Z]+) (CAPITAL|SMALL) LETTER (.*)", self.name):
            self.type = m.group(1)
            self.capital = m.group(2) == "CAPITAL"
            letter_name = m.group(3)
            if m := re.match(r"(.*) WITH", letter_name):
                self.letter_name = m.group(1)
            else:
                self.letter_name = letter_name
        else:
            self.type = ""
            self.capital = False
            self.letter_name = ""

    def __str__(self):
        return f"{self.char} [U+{self.code:04x}] {self.name}"
    
    def json(self):
        return {
            "code": f"{self.code:04x}",
            "nfd": " ".join([f"{ord(ch):04x}" for ch in self.nfd]),
            "name": self.name,
        }

# Read Unicode names
letters_info = {}
for s, e in [(0x20, 0x250), (0x1e00, 0x1f00), (0x384, 0x3d0), (0x1f00, 0x2000)]:
    for code in range(s, e):
        uch = UnicodeChar(code)
        if uch.type:
            letters_info[uch.char] = uch
latin_letters_info = {key: uch for key, uch in letters_info.items() if uch.type == "LATIN"}
greek_letters_info = {key: uch for key, uch in letters_info.items() if uch.type == "GREEK"}

# extract: GREEK CAPITAL/SMALL LETTER
greek_capital_letters = "".join([uch.char for uch in greek_letters_info.values() if uch.capital])
greek_small_letters = "".join([uch.char for uch in greek_letters_info.values() if not uch.capital])
greek_letters = greek_capital_letters + greek_small_letters

attr_chars = {}

def collect_attrs(letters_info):
    ret = {"": ""}
    for key in sorted(letters_info.keys()):
        uch = letters_info[key]
        if len(uch.nfd) == 1:
            ret[""] += uch.char
        for ch in uch.nfd[1:]:
            if ch not in attr_chars:
                attr_chars[ch] = (unicodedata.name(ch)
                                  .replace("COMBINING ", "")
                                  .replace(" ", "_"))
            name = attr_chars[ch]
            if name not in ret:
                ret[name] = ""
            ret[name] += uch.char
    return ret

latin_attrs = collect_attrs(latin_letters_info)
greek_attrs = collect_attrs(greek_letters_info)
attr_chars_rev = {name: ch for ch, name in attr_chars.items()}

def is_letter(letter):
    return letter in greek_letters

def is_vowel(letter):
    uch = greek_letters_info.get(letter)
    return uch.nfd[0] in "ΑΕΗΙΟΥΩαεηιουω" if uch else False

def is_consonant(letter):
    return is_letter(letter) and not is_vowel(letter)

greek_vowels = "".join(filter(is_vowel, greek_letters))
greek_consonants = "".join(filter(is_consonant, greek_letters))

greek_basic_letters = "αβγδεζηθικλμνξοπρςστυφχψω"
romanize_basic = "a,b,g,d,e,z,ē,th,i,c,l,m,n,x,o,p,r,s,s,t,y,ph,ch,ps,ō".split(",")
romanize_basic_table = {gch: unicodedata.normalize("NFD", lch)
                        for gch, lch in zip(greek_basic_letters, romanize_basic)}

def romanize1(letter):
    if letter in "\u00b7\u0387":
        return ";"
    if letter == ";":
        return "?"
    nfd = unicodedata.normalize("NFD", letter.lower())
    if not (ret := romanize_basic_table.get(nfd[0])):
        return letter
    if macron := (ret[-1] == attr_chars_rev["MACRON"]):
        ret = ret[:-1]
    if attr_chars_rev["REVERSED_COMMA_ABOVE"] in nfd:
        if ret == "r":
            ret += "h"
        else:
            ret = "h" + ret
    if (ch := attr_chars_rev["DIAERESIS"]) in nfd:
        ret += ch
    circ = attr_chars_rev["GREEK_PERISPOMENI"] in nfd
    iota = attr_chars_rev["GREEK_YPOGEGRAMMENI"] in nfd
    ch = attr_chars_rev["MACRON"]
    if not circ and not iota and (macron or ch in nfd):
        ret += ch
    for name in ["BREVE", "ACUTE_ACCENT", "GRAVE_ACCENT"]:
        if (ch := attr_chars_rev[name]) in nfd:
            ret += ch
    if circ:
        ret += attr_chars_rev["CIRCUMFLEX_ACCENT"]
    if iota:
        ret += attr_chars_rev["DOT_BELOW"]
    ret = unicodedata.normalize("NFC", ret)
    return ret if letter.islower() else ret.capitalize()

romanization_table = {
    "\u00b7": ";", # MIDDLE DOT
    "\u0387": ";", # GREEK ANO TELEIA
    ";": "?",
}
for ch in greek_small_letters:
    romanization_table[ch] = romanize1(ch)

table_name = "romanize"
with open(f"json/{table_name}-extra.json", "r", encoding="utf-8") as file:
    romanization_table_ex = json.load(file)

romanization_table_ex["caron"] = {
    unicodedata.normalize("NFC", key): unicodedata.normalize("NFC", value)
    for key, value in romanization_table_ex["caron"].items()
}
romanization_table_ex["dotMacron"] = {
    unicodedata.normalize("NFC", key): unicodedata.normalize("NFC", value)
    for key, value in romanization_table_ex["dotMacron"].items()
}

def reverse_table(table):
    rev = {}
    for key, value in table.items():
        if value not in rev:
            rev[value] = ""
        rev[value] += key
    return rev

# Generate Unicode Data
with open("json/unicode-latin.json", "w", encoding="utf-8") as file:
    json.dump({key: uch.json() for key, uch in latin_letters_info.items()}, file, ensure_ascii=False, indent=2)
with open("json/unicode-greek.json", "w", encoding="utf-8") as file:
    json.dump({key: uch.json() for key, uch in greek_letters_info.items()}, file, ensure_ascii=False, indent=2)

# convert to JSON
table = json.dumps({
    "greekLetters": greek_letters,
    "greekCapitalLetters": greek_capital_letters,
    "greekSmallLetters": greek_small_letters,
    "attributes": greek_attrs,
    "attributeCodes": {name: f"{ord(ch):04x}" for ch, name in attr_chars.items() if name in greek_attrs},
    "greekVowels": greek_vowels,
    "greekConsonants": greek_consonants,
    "romanizationTableRev": reverse_table(romanization_table),
    "romanizationTableEx": romanization_table_ex,
}, ensure_ascii=False, indent=2)

# Save to file
with open(f"json/{table_name}.json", "w", encoding="utf-8") as file:
    file.write(table)

# Generate JavaScript module
with open(f"{table_name}.js", "w", encoding="utf-8") as file:
    file.write(f"export const table = {table};");

# Generate Python module
with open(f"{table_name}.py", "w", encoding="utf-8") as file:
    file.write(f"table = {table}");

### unit test

import unittest, greektrans

def load_texts(file_prefix):
    with open(f"{file_prefix}.txt", "r", encoding="utf-8") as file:
        src = file.read()
    with open(f"{file_prefix}-romanized.txt", "r", encoding="utf-8") as file:
        dst_r = file.read()
    with open(f"{file_prefix}-monotonized.txt", "r", encoding="utf-8") as file:
        dst_m = file.read()
    return src, dst_r, dst_m

class TestGreekTrans(unittest.TestCase):
    def test(self):
        self.assertEqual(greektrans.strip("ᾅ"), "α")
        self.assertEqual(greektrans.strip("ί"), "ι")
        self.assertEqual(greektrans.prepare_romanize("κἀγώ"), "κἀ'γώ")

        src = "Ἐγὼ δ' εἰς τὴν ἀγρίαν ὁδὸν εἰσῆλθον."
        self.assertEqual(greektrans.strip(src),
                         "Εγω δ' εις την αγριαν οδον εισηλθον.")
        self.assertEqual(greektrans.romanize(src),
                         "Egṑ d' eis tḕn agrían hodòn eisêlthon.")

    # The Lord's Prayer
    # https://en.wikipedia.org/wiki/Greek_diacritics#Examples
    def test_lords_prayer(self):
        src, dst_r, dst_m = load_texts("samples/lords_prayer")
        self.assertEqual(greektrans.romanize(src), dst_r)
        self.assertEqual(greektrans.monotonize(src), dst_m)

    # Divine Comedy Inferno Canto 1
    # https://github.com/7shi/dante-la-el
    def test_inferno_1(self):
        src, dst_r, dst_m = load_texts("samples/inferno-1")
        self.assertEqual(greektrans.romanize(src), dst_r)
        self.assertEqual(greektrans.monotonize(src), dst_m)

unittest.main()
