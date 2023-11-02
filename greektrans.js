// Greek character conversion utility

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

const romanizationTable = fromReversedTable(table.romanizationTableRev);

const attributeCodes = {};
for (const [key, value] of Object.entries(table["attributeCodes"])) {
    attributeCodes[key] = String.fromCharCode(parseInt(value, 16));
}

const greekAttrsChar = {};
for (const [key, value] of Object.entries(attributeCodes)) {
    if (key == "TONOS" || key == "OXIA" || key == "PERISPOMENI") {
        greekAttrsChar[value] = attributeCodes.TONOS;
    } else if (key == "DIALYTIKA") {
        greekAttrsChar[value] = attributeCodes.DIALYTIKA;
    } else {
        greekAttrsChar[value] = "";
    }
}

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

export function monotonize(text) {
    text = text.normalize("NFD");
    text = replaces(greekAttrsChar, text);
    return text.normalize("NFC");
}

function prepareRomanize(word) {
    let ret = "";
    if (word.length >= 1 && isVowel(word[0])) {
        if (word.length >= 2 && table.romanizationTableEx.combination[word.slice(0, 2)]) {
            ret = word.slice(0, 2);
            word = word.slice(2);
        } else {
            ret = word.slice(0, 1);
            word = word.slice(1);
        }
    }
    // check coronis: ex. κἀγώ = καὶ ἐγώ
    const psili = table.attributes.PSILI;
    for (const ch of word) {
        ret += ch;
        if (psili.includes(ch)) ret += "'";
    }
    return ret;
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

export function romanize(text, caron = true, dotMacron = true) {
    let ret = "";
    for (const [type, token] of tokenize(text)) {
        if (type === 1) {
            ret += prepareRomanize(token);
        } else {
            ret += token;
        }
    }
    ret = replaces(table.romanizationTableEx.combination, ret);
    ret = replaces(romanizationTable, ret);
    if (caron) {
        ret = replaces(table.romanizationTableEx.caron, ret);
    }
    if (dotMacron) {
        ret = replaces(table.romanizationTableEx.dotMacron, ret);
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
