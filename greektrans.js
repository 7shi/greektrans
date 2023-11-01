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
    return letter in table.greekLetters;
}

export function isVowel(letter) {
    return letter in table.greekVowels;
}

export function isConsonant(letter) {
    return letter in table.greekConsonants;
}

function stringMap(map, text) {
    return text.split("").map((letter) => map[letter] || letter).join("");
}

export function strip(text) {
    return stringMap(stripTable, text);
}

export function toMonotonic(text) {
    return stringMap(monotonicTable, text);
}

function replaces(table, text) {
    for (const [key, value] of Object.entries(table)) {
        text = text.replaceAll(key, value);
    }
    return text;
}

export function romanize(text, caron = true, dotMacron = true) {
    text = replaces(table.romanizationTableEx.combination, text);
    text = stringMap(romanizationTable, text);
    if (caron) {
        text = replaces(table.romanizationTableEx.caron, text);
    }
    if (dotMacron) {
        text = replaces(table.romanizationTableEx.dotMacron, text);
    }
    return text;
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
            console.log((monotonic ? toMonotonic : romanize)(text).trimEnd());
        } catch (e) {
            console.error(e);
            Deno.exit(1);
        }
    }
}

