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

        self.attrs = set()
        if m := re.match(r"(.*) WITH (.*)", self.name):
            self.base_name = m.group(1)
            for attr in m.group(2).split(" AND "):
                self.attrs.add(attr)
        else:
            self.base_name = self.name

        # Latin attributes
        self.acute      = "ACUTE"      in self.attrs
        self.grave      = "GRAVE"      in self.attrs
        self.circumflex = "CIRCUMFLEX" in self.attrs
        self.diaeresis  = "DIAERESIS"  in self.attrs # tréma, umlaut
        self.macron     = "MACRON"     in self.attrs
        self.breve      = "BREVE"      in self.attrs
        self.caron      = "CARON"      in self.attrs # háček
        self.dot_below  = "DOT BELOW"  in self.attrs

        # Greek attributes
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

def search(type, name, capital, *attrs):
    base_name = type + " " + ("CAPITAL" if capital else "SMALL") + " LETTER " + name
    attrs_set = set(attrs)
    for uch in letters_info.values():
        if uch.base_name == base_name and uch.attrs == attrs_set:
            return uch
    return None

# extract: GREEK CAPITAL/SMALL LETTER
greek_capital_letters = "".join([uch.char for uch in greek_letters_info.values() if uch.capital])
greek_small_letters = "".join([uch.char for uch in greek_letters_info.values() if not uch.capital])
greek_letters = greek_capital_letters + greek_small_letters

attr_chars = {}

def collect_attrs(letters):
    ret = {"": ""}
    for uch in letters:
        if len(uch.attrs) == 0:
            ret[""] += uch.char
        else:
            for attr in uch.attrs:
                if attr not in ret:
                    ret[attr] = ""
                ret[attr] += uch.char
            if len(uch.attrs) == 1:
                attr = list(uch.attrs)[0]
                hexstr = " ".join([f"{ord(ch):04x}" for ch in uch.nfd])
                if len(uch.nfd) == 2:
                    if attr not in attr_chars:
                        attr_chars[attr] = uch.nfd[1]
                    elif attr_chars[attr] != uch.nfd[1]:
                        raise Exception(f"Unexpected NFD: {uch} ({hexstr})")
                else:
                    # print(f"Length not 2 ({hexstr}): {uch}")
                    pass
    return ret

latin_attrs = collect_attrs(latin_letters_info.values())
greek_attrs = collect_attrs(greek_letters_info.values())
# print("attr_chars:", {key: [f"{ord(ch):04x}" for ch in value] for key, value in attr_chars.items()})
greek_attrs_char = [attr_chars[attr] for attr in greek_attrs.keys() if attr]

def add_attr(ch, attr):
    if not (uch := letters_info.get(ch)):
        raise Exception(f"Unknown character: {ch}")
    if not (ach := attr_chars.get(attr)):
        raise Exception(f"Unknown attribute: {attr}")
    ret = search(uch.type, uch.letter_name, uch.capital, *uch.attrs.union({attr}))
    return ret.char if ret else ch + ach

def monotonize1(letter):
    if not (uch := greek_letters_info.get(letter)):
        return letter
    ret = uch.nfd[0]
    if uch.dialytika:
        if ch := add_attr(ret, "DIALYTIKA"):
            ret = ch
    if uch.tonos or uch.perispomeni or uch.oxia:
        if ch := add_attr(ret, "TONOS"):
            ret = ch
    return ret

monotonic_table = {key: key2 for key in greek_letters if key != (key2 := monotonize1(key))}

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
romanize_basic_table = {greek_letters_info[lch].letter_name: gch for lch, gch in zip(greek_basic_letters, romanize_basic)}

# Create romanization table template
table_name = "romanize"
if not os.path.exists(f"json/{table_name}-letter.json"):
    with open(f"json/{table_name}-letter.json", "w", encoding="utf-8") as file:
        json.dump({letter: "" for letter in greek_letters}, file, ensure_ascii=False, indent=2)
    print(f"Please edit `json/{table_name}-letter.json`.", file=sys.stderr)
    sys.exit(1)

with open(f"json/{table_name}-letter.json", "r", encoding="utf-8") as file:
    romanization_table = json.load(file)

with open(f"json/{table_name}-extra.json", "r", encoding="utf-8") as file:
    romanization_table_ex = json.load(file)

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
    "attributeCodes": {attr: f"{ord(attr_chars[attr]):04x}" for attr in greek_attrs.keys() if attr},
    "greekVowels": greek_vowels,
    "greekConsonants": greek_consonants,
    "monotonicTableRev": reverse_table(monotonic_table),
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
