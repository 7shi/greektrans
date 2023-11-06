# greektrans

Ancient Greek Transliteration Tools.

Available in Python and JavaScript, it can be used as a library and a command line tool. It supports romanization and Modern Greek-like (but not fully compliant) accent monotonization.

Online Demo

* https://codepen.io/7shi/pen/rNPLdaP

# Specification

## Romanization

Priority was given to the ease of recalling the spelling when Greek vocabulary was incorporated into English via Latin.

The transliteration rule is based on the Classical method. (except "ει" -> "ei")

* https://en.wikipedia.org/wiki/Romanization_of_Greek#Ancient_Greek

Diacritical mark conversions are in the original system. Some rules can be disabled by the argument of `romanize`.

* The circumflex accent on the diphthong is split into acute and grave.  
  ex. "πνεῦμα" -> "pnéùma" ("eû" -> "éù")
* The caron is used for the acute accent on the long vowel. (`caron` argument)  
  ex. "φωνή" -> "phōně" ("ḗ" -> "èé" -> "ě")
* The dot below is used for the iota subscript.  
  ex. "λόγῳ" -> "lógọ̄"
* The apostrophe is used for the coronis.  
  ex. "κἀγώ" -> "ca'gǒ"

The dot below was chosen because the font composition is relatively supported compared to the other diacritical marks.

The vowel with the iota subscript is always long, so the macron is redundant. But it seems better to add this for those who are not familiar with it. (`dotMacron` argument)

## Monotonize

Monotonization integrates the acute and grave and circumflex accent into the acute accent in polysyllabic words. The accents in monosyllabic words and other diacritic marks are omitted.

The Wikipedia's example is reproduced.

* https://en.wikipedia.org/wiki/Greek_diacritics#Examples

But it does not take into account Modern Greek grammar and therefore does not conform to its orthography. For example, it cannot distinguish between [η](https://en.wiktionary.org/wiki/%CE%B7#Greek) "the" and [ή](https://en.wiktionary.org/wiki/%CE%AE#Greek) "or".

# Usage

## Command Line

`-m` option specifies to monotonize.

```sh
python greektrans.py [-m] file
```

or

```sh
deno run --allow-read greektrans.js [-m] file
```

## Python

Use as library.

```py
import greektrans

text = "Πάτερ ἡμῶν ὁ ἐν τοῖς οὐρανοῖς·"

print(greektrans.romanize(text))
# Páter hēmôn ho en tóès ūranóès;

print(greektrans.monotonize(text))
# Πάτερ ημών ο εν τοις ουρανοίς·
```

## JavaScript

Supports the browser and Deno.

```js
import * as greektrans from "https://cdn.jsdelivr.net/gh/7shi/greektrans@0.6/greektrans.min.js";

const text = "Πάτερ ἡμῶν ὁ ἐν τοῖς οὐρανοῖς·";

console.log(greektrans.romanize(text));
// Páter hēmôn ho en tóès ūranóès;

console.log(greektrans.monotonize(text));
// Πάτερ ημών ο εν τοις ουρανοίς·
```

# Links

Examples of use. (translation is inaccurate)

* https://github.com/7shi/dante-la-el/blob/main/Inferno/ChatGPT/02-grc-words.md

Description of technology used. (in Japanese)

* https://qiita.com/7shi/items/6000e9ce33145bec49a0

Explanation of motive. (in Japanese)

* https://7shi.hateblo.jp/entry/2023/11/04/005458
