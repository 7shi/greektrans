# Normalize Greek punctuation

import sys

if len(sys.argv) < 2:
    print(f"Usage: python {sys.argv[0]} <file>", file=sys.stderr)
    sys.exit(1)

# References:
# https://en.wiktionary.org/wiki/Appendix:Greek_punctuation

with open(sys.argv[1], "r", encoding="utf-8") as f:
    for line in f:
        line = (line
            # raised point
            .replace("·", "·") # U+0387 GREEK ANO TELEIA

            # apostrophe: It takes the place of a vowel which is omitted in pronunciation.
            .replace("᾽ ", "' ") # U+1FBD GREEK KORONIS
            .replace("᾿ ", "' ") # U+1FBF GREEK PSILI
            .replace("’ ", "' ") # U+2019 RIGHT SINGLE QUOTATION MARK
        )
        print(line, end="")
