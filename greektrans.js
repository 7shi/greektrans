// Greek character conversion utility

import { table } from "./romanize.js";

function fromReverseTable(tableRev) {
    const table = {};
    for (const [key, value] of Object.entries(tableRev)) {
        for (const letter of value) {
            table[letter] = key;
        }
    }
    return table;
}

const stripTable = fromReverseTable(table.stripTableRev);
const monotonicTable = fromReverseTable(table.monotonicTableRev);
const romanizationTable = fromReverseTable(table.romanizationTableRev);

export function isLetter(letter) {
    return table.greekLetters.includes(letter);
}

export function isVowel(letter) {
    return table.greekVowels.includes(letter);
}

export function isConsonant(letter) {
    return table.greekConsonants.includes(letter);
}

function stringMap(map, text) {
    return text.split("").map((letter) => map[letter] || letter).join("");
}

export function strip(text) {
    return stringMap(stripTable, text);
}

export function monotonize(text) {
    return stringMap(monotonicTable, text);
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

function replaces(table, text) {
    for (const [key, value] of Object.entries(table)) {
        text = text.replaceAll(key, value);
    }
    return text;
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
    ret = stringMap(romanizationTable, ret);
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
