# Create a table of Greek letters

import re, json, unicodedata

# read Unicode names
letter_names = {}
for s, e in [(0x20, 0x250), (0x1e00, 0x1f00), (0x384, 0x3d0), (0x1f00, 0x2000)]:
    for code in range(s, e):
        ch = chr(code)
        name = unicodedata.name(ch, "")
        if re.match(r"(LATIN|GREEK) .* LETTER", name):
            letter_names[ch] = name
latin_letter_names = {key: value for key, value in letter_names.items() if value.startswith("LATIN")}
greek_letter_names = {key: value for key, value in letter_names.items() if value.startswith("GREEK")}

# extract: GREEK CAPITAL/SMALL LETTER
greek_capital_letters = "".join([ch for ch, name in greek_letter_names.items() if "CAPITAL" in name])
greek_small_letters   = "".join([ch for ch, name in greek_letter_names.items() if "SMALL"   in name])
greek_letters = greek_capital_letters + greek_small_letters

attr_chars = {}

def collect_attrs(letter_names):
    ret = {"": ""}
    for ch in sorted(letter_names.keys()):
        name = letter_names[ch]
        nfd = unicodedata.normalize("NFD", ch)
        if len(nfd) == 1:
            ret[""] += ch
        for attr in nfd[1:]:
            if attr not in attr_chars:
                attr_chars[attr] = (unicodedata.name(attr)
                                    .replace("COMBINING ", "")
                                    .replace(" ", "_"))
            name = attr_chars[attr]
            if name not in ret:
                ret[name] = ""
            ret[name] += ch
    return ret

latin_attrs = collect_attrs(latin_letter_names)
greek_attrs = collect_attrs(greek_letter_names)
attr_chars_rev = {name: ch for ch, name in attr_chars.items()}

def is_letter(letter):
    return letter in greek_letters

def is_vowel(letter):
    nfd = unicodedata.normalize("NFD", letter)
    return nfd[0] in "ΑΕΗΙΟΥΩαεηιουω"

def is_consonant(letter):
    return is_letter(letter) and not is_vowel(letter)

greek_vowels = "".join(filter(is_vowel, greek_letters))
greek_consonants = "".join(filter(is_consonant, greek_letters))

### Romanize

greek_basic_letters = "αβγδεζηθικλμνξοπρςστυφχψω"
romanize_basic = "a,b,g,d,e,z,ē,th,i,c,l,m,n,x,o,p,r,s,s,t,y,ph,ch,ps,ō".split(",")
romanize_basic_table = {gch: unicodedata.normalize("NFD", lch)
                        for gch, lch in zip(greek_basic_letters, romanize_basic)}

def add_attr(text, attr):
    ch = attr_chars_rev[attr]
    nfc = unicodedata.normalize("NFC", text)
    if len(nfc) == 1:
        nfc2 = unicodedata.normalize("NFC", text + ch)
        if len(nfc2) == 1 or nfc2[-1] == ch:
            return nfc2
    return nfc + ch

def romanize1(letter):
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
    if letter.isupper():
        ret = ret.capitalize()
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
        return add_attr(ret, "DOT_BELOW")
    return unicodedata.normalize("NFC", ret)

romanization_table = {
    "\u00b7": ";", # MIDDLE DOT
    "\u0387": ";", # GREEK ANO TELEIA
    ";": "?",
}
for ch in greek_small_letters:
    romanization_table[ch] = romanize1(ch)

# extra tables

def make_letter(base_letter, *attrs):
    ret = base_letter
    for attr in attrs:
        ret += attr_chars_rev[attr]
    return ret

combination = {}
for s, d in [("αι", ["a", "e"]), ("ει", ["e", "i"]), ("υι", ["y", "i"]), ("οι", ["o", "e"]),
             ("αυ", ["a", "u"]), ("ευ", ["e", "u"]), ("ηυ", ["ē", "u"]), ("ου", ["", "ū"])]:
    for asp in [[], ["COMMA_ABOVE"], ["REVERSED_COMMA_ABOVE"]]:
        for acc in [[], ["ACUTE_ACCENT"], ["GRAVE_ACCENT"], ["GREEK_PERISPOMENI"]]:
            s1 = s[0:-1]
            s2 = unicodedata.normalize("NFC", make_letter(s[-1], *asp, *acc))
            d0 = "h" if asp == ["REVERSED_COMMA_ABOVE"] else ""
            circ = acc == ["GREEK_PERISPOMENI"]
            d1 = add_attr(d[0], "ACUTE_ACCENT") if d[0] and circ else d[0]
            dacc = ["GRAVE_ACCENT" if d1 else "CIRCUMFLEX_ACCENT"] if circ else acc
            d2 = d[1][0]
            if dacc:
                d2 = unicodedata.normalize("NFD", d2)
                if circ:
                    d2 = d2[0]
                d2 = add_attr(d2, *dacc)
            d3 = d[1][1:]
            ss = s1 + s2
            dd = d0 + d1 + d2 + d3
            combination[ss] = dd
for s, d in [("γγ", "ng"), ("γκ", "nc"), ("γξ", "nx"), ("γχ", "nch")]:
    combination[s] = d

caron = {}
for ch in "aeo": # ACUTE + DOT -> CARON + DOT
    ch1 = add_attr(make_letter(ch, "ACUTE_ACCENT"), "DOT_BELOW")
    ch2 = add_attr(make_letter(ch, "CARON"       ), "DOT_BELOW")
    caron[ch1] = ch2
for ch in "eou": # MACRON + ACUTE -> CARON
    ch1 = add_attr(make_letter(ch, "MACRON"), "ACUTE_ACCENT")
    ch2 = add_attr(ch, "CARON")
    caron[ch1] = ch2

dot_macron = {}
for ch in "aeo":
    for acc in [[], ["ACUTE_ACCENT"], ["GRAVE_ACCENT"]]:
        ch1 = add_attr(make_letter(ch,           *acc), "DOT_BELOW")
        ch2 = add_attr(make_letter(ch, "MACRON", *acc), "DOT_BELOW")
        dot_macron[ch1] = ch2

def check_assoc(a, b):
    ok = True
    for key, value in a.items():
        if key not in b:
            print(f"missing: {key}: {value} not in b")
            ok = False
        elif value != b[key]:
            print(f"conflict: {key} {value} != {b[key]}")
            ok = False
    for key, value in b.items():
        if key not in a:
            print(f"missing: {key}: {value} not in a")
            ok = False
    return ok

### Save table

def reverse_table(table):
    rev = {}
    for key, value in table.items():
        if value not in rev:
            rev[value] = ""
        rev[value] += key
    return rev

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
    "combination": combination,
    "caron": caron,
    "dotMacron": dot_macron,
}, ensure_ascii=False, indent=2)

table_name = "romanize"

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
