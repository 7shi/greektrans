# greektrans

Ancient Greek Transliteration Tools.

Available in Python and JavaScript, it can be used as a library and a command line tool. It supports romanization and Modern Greek-like (but not fully compliant) accent monotonization.

Online Demo: https://codepen.io/7shi/pen/rNPLdaP

# Specification

## Romanization

Priority was given to the ease of recalling the spelling when Greek vocabulary was incorporated into English via Latin.

The transliteration rule is based on the Classical method. (except "ει" -> "ei")

* https://en.wikipedia.org/wiki/Romanization_of_Greek#Ancient_Greek

Diacritical mark conversions are in the original system.

* The circumflex accent on the diphthong is split into acute and grave.  
  ex. "πνεῦμα" -> "pnéùma" ("eû" -> "éù")
* The caron is used for the acute accent on the long vowel.  
  ex. "φωνή" -> "phōně" ("ḗ" -> "èé" -> "ě")
* The dot below is used for the iota subscript.  
  ex. "λόγῳ" -> "lógọ̄"
* The apostrophe is used for the coronis.  
  ex. "κἀγώ" -> "ca'gǒ"

The dot below was chosen because the font composition is relatively supported compared to the other diacritical marks.

The vowel with the iota subscript is always long, so the macron is redundant. But it seems better to add this for those who are not familiar with it.

## Monotonize

Monotonization integrates the acute and circumflex accent into the acute accent. Other diacritic marks are omitted.

It does not take into account Modern Greek grammar and therefore does not conform to its orthography.

The Wikipedia's example is not reproduced.

* https://en.wikipedia.org/wiki/Greek_diacritics#Examples

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

## JavaScript

Supports the browser and Deno.

```js
import * as greektrans from "https://cdn.jsdelivr.net/gh/7shi/greektrans@0.4/greektrans.min.js";

const text = "Πάτερ ἡμῶν ὁ ἐν τοῖς οὐρανοῖς·";

console.log(greektrans.romanize(text));
// => "Páter hēmôn ho en tóès ūranóès;"

console.log(greektrans.monotonize(text));
// => "Πάτερ ημών ο εν τοίς ουρανοίς·"
```
