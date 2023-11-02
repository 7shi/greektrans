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

greek_nfd_rev = {}
for key in sorted(greek_letters_info.keys()):
    uch = greek_letters_info[key]
    nfd = "".join(sorted(uch.nfd))
    if nfd not in greek_nfd_rev:
        greek_nfd_rev[nfd] = uch.char

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

def strip1(letter):
    uch = greek_letters_info.get(letter)
    return uch.nfd[0] if uch else letter

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
    "greekNFD": {key: " ".join([f"{ord(ch):04x}" for ch in value.nfd]) for key, value in greek_letters_info.items()},
    "greekVowels": greek_vowels,
    "greekConsonants": greek_consonants,
    "stripTableRev": reverse_table(strip_table),
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

### Additional Impementation

def normalize_nfd(text):
    ret = ""
    for ch in text:
        if uch := greek_letters_info.get(ch):
            ret += uch.nfd
        else:
            ret += ch
    return ret

def normalize_nfc1(chs):
    for length in range(len(chs), 0, -1):
        if ch := greek_nfd_rev.get("".join(sorted(chs[:length]))):
            return ch + chs[length:]
    return chs

def normalize_nfc(text):
    ret = ""
    chs = ""
    for ch in text:
        if ch not in greek_attrs_char:
            if chs:
                ret += normalize_nfc1(chs)
                chs = ""
        chs += ch
    if chs:
        ret += normalize_nfc1(chs)
    return ret

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
    psili = greek_attrs["PSILI"]
    for ch in word:
        ret += ch
        if ch in psili:
            ret += "'"
    return ret

def tokenize(text):
    text = normalize_nfc(text)
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
        self.assertEqual(prepare_romanize("κἀγώ"), "κἀ'γώ")

        src = "ᾅ"
        nfd = unicodedata.normalize("NFD", src)
        self.assertEqual(normalize_nfd (src), nfd)
        self.assertEqual(normalize_nfc1(nfd), src)
        self.assertEqual(normalize_nfc (nfd), src)

        src = "ί"
        nfd = unicodedata.normalize("NFD", src)
        self.assertEqual(normalize_nfd (src), nfd)
        self.assertEqual(normalize_nfc1(nfd), src)
        self.assertEqual(normalize_nfc (nfd), src)

        src = "Ἐγὼ δ' εἰς τὴν ἀγρίαν ὁδὸν εἰσῆλθον."
        self.assertEqual(romanize(src), "Egṑ d' eis tḕn agrían hodòn eisêlthon.")
        nfd = unicodedata.normalize("NFD", src)
        self.assertEqual(normalize_nfd(src), nfd)
        self.assertEqual(normalize_nfc(nfd), unicodedata.normalize("NFC", nfd))

    # The Lord's Prayer
    # https://en.wikipedia.org/wiki/Greek_diacritics#Examples
    def test_lords_prayer(self):
        src, dst_r, dst_m = load_texts("samples/lords_prayer")
        self.assertEqual(romanize(src), dst_r)
        self.assertEqual(monotonize(src), dst_m)
        nfd = unicodedata.normalize("NFD", src)
        self.assertEqual(normalize_nfd(src), nfd)
        self.assertEqual(normalize_nfc(nfd), unicodedata.normalize("NFC", nfd))

    # Divine Comedy Inferno Canto 1
    # https://github.com/7shi/dante-la-el
    def test_inferno_1(self):
        src, dst_r, dst_m = load_texts("samples/inferno-1")
        self.assertEqual(romanize(src), dst_r)
        self.assertEqual(monotonize(src), dst_m)

unittest.main()
