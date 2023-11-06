// Greek character conversion utility

/// initialize table

import { table } from "./romanize.js";

function fromReversedTable(tableRev) {
    const table = {};
    for (const [key, value] of Object.entries(tableRev)) {
        for (const letter of value) {
            table[letter] = key;
        }
    }
    return table;
}

function capitalize(text) {
    return text[0].toUpperCase() + text.slice(1);
}

const romanizationTable = fromReversedTable(table.romanizationTableRev);
for (const ch of table.greekCapitalLetters) {
    romanizationTable[ch] = capitalize(romanizationTable[ch.toLowerCase()]);
}

const attributeCodes = {};
for (const [key, value] of Object.entries(table["attributeCodes"])) {
    attributeCodes[key] = String.fromCharCode(parseInt(value, 16));
}

const greekAttrsChar = {};
for (const [key, value] of Object.entries(attributeCodes)) {
    if (["ACUTE_ACCENT", "GRAVE_ACCENT", "GREEK_PERISPOMENI"].includes(key)) {
        greekAttrsChar[value] = attributeCodes.ACUTE_ACCENT;
    } else if (key == "DIAERESIS") {
        greekAttrsChar[value] = attributeCodes.DIAERESIS;
    } else {
        greekAttrsChar[value] = "";
    }
}

function isDecomposed(text) {
    return text == text.normalize("NFD");
}

function hasAttr(text, attr) {
    return text.normalize("NFD").includes(attributeCodes[attr]);
}

const combinationTable = {}
const diphthongs = {}
for (const [key, value] of Object.entries(table.combination)) {
    combinationTable[key] = value;
    if (isDecomposed(key)) {
        combinationTable[key.toUpperCase()] = value.toUpperCase();
    } else if (value[0] === "h" || hasAttr(key, "COMMA_ABOVE")) {
        combinationTable[capitalize(key)] = capitalize(value);
    }
    if (key.normalize("NFD").length == 2 && table.greekVowels.includes(key[0])) {
        diphthongs[key] = "α"
    }
}

function addUpper(table) {
    for (const [key, value] of Object.entries(table)) {
        table[key.toUpperCase()] = value.toUpperCase();
    }
}

addUpper(table.caron);
addUpper(table.dotMacron);

/// utility functions

export function isLetter(letter) {
    return table.greekLetters.includes(letter);
}

export function isVowel(letter) {
    return table.greekVowels.includes(letter);
}

export function isConsonant(letter) {
    return table.greekConsonants.includes(letter);
}

export function strip(text) {
    text = text.normalize("NFD");
    for (const ch in greekAttrsChar) {
        text = text.replaceAll(ch, "")
    }
    return text.normalize("NFC");
}

function replaces(table, text) {
    for (const [key, value] of Object.entries(table)) {
        if (key != value) text = text.replaceAll(key, value);
    }
    return text;
}

function* tokenize(text) {
    text = text.normalize("NFC");
    let token = "";
    let type = 0;
    for (const ch of text) {
        const t = isLetter(ch) ? 1 : 2;
        if (type !== t) {
            if (token) {
                yield [type, token];
                token = "";
            }
            type = t;
        }
        token += ch;
    }
    if (token) yield [type, token];
}

function prepareMonotonize(word) {
    const w = strip(word);
    if (Array.from(replaces(diphthongs, w)).filter(isVowel).length < 2) {
        return w;
    }
    return word;
}

export function monotonize(text) {
    let ret = "";
    for (const [type, token] of tokenize(text)) {
        if (type === 1) {
            ret += prepareMonotonize(token);
        } else {
            ret += token;
        }
    }
    ret = ret.normalize("NFD");
    ret = replaces(greekAttrsChar, ret);
    return ret.normalize("NFC");
}

function prepareRomanize(word) {
    let ret = "";
    if (word.length >= 1 && isVowel(word[0])) {
        if (word.length >= 2 && combinationTable[word.slice(0, 2)]) {
            ret = word.slice(0, 2);
            word = word.slice(2);
        } else {
            ret = word.slice(0, 1);
            word = word.slice(1);
        }
    }
    // check coronis: ex. κἀγώ = καὶ ἐγώ
    const psili = table.attributes.COMMA_ABOVE;
    for (const ch of word) {
        ret += ch;
        if (psili.includes(ch)) ret += "'";
    }
    return ret;
}

export function romanize(text, caron = true, dotMacron = true) {
    let ret = "";
    for (const [type, token] of tokenize(text)) {
        if (type === 1) {
            ret += prepareRomanize(token);
        } else {
            ret += token;
        }
    }
    ret = replaces(combinationTable, ret);
    ret = [...ret].map(letter => romanizationTable[letter] || letter).join("");
    if (caron) {
        ret = replaces(table.caron, ret);
    }
    if (dotMacron) {
        ret = replaces(table.dotMacron, ret);
    }
    return ret;
}

if (import.meta.main) {
    let file, monotonic = false;
    if (Deno && Deno.args && Deno.args.length) {
        if (Deno.args[0] == "-m") {
            monotonic = true;
            file = Deno.args[1];
        } else {
            file = Deno.args[0];
        }
    }
    if (!file) {
        console.error("usage: deno run --allow-read el-utils.js [-m] input_file");
        if (Deno) Deno.exit(1);
    } else {
        try {
            const text = Deno.readTextFileSync(file);
            console.log((monotonic ? monotonize : romanize)(text).trimEnd());
        } catch (e) {
            console.error(e);
            Deno.exit(1);
        }
    }
}
