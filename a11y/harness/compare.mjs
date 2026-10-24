#!/usr/bin/env node
// Compares two harness runs and prints per page and per success criterion deltas.
//
// Usage: node compare.mjs <before> <after>
//   <before>/<after> are run folders (out-post-theme/, out/) or summary-by-sc.json files.
//   When both folders also hold summary-checks.json, the scripted-check counters are compared too.
import fs from 'node:fs';
import path from 'node:path';

const [beforeArg, afterArg] = process.argv.slice(2);

if (beforeArg == null || afterArg == null) {
    console.error('Usage: node compare.mjs <before run folder or summary-by-sc.json> <after run folder or summary-by-sc.json>');
    process.exit(2);
}

const summaryFile = (p) => (fs.statSync(p).isDirectory() ? path.join(p, 'summary-by-sc.json') : p);
const checksFile = (p) => path.join(fs.statSync(p).isDirectory() ? p : path.dirname(p), 'summary-checks.json');
const readJson = (f) => (fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : null);

// Flattens {sc: [{role, page, rule, nodes}]} into Map("role/page" -> Map("sc rule" -> nodes)).
function byPage(summary) {
    const pages = new Map();

    for (const [sc, rows] of Object.entries(summary ?? {})) {
        for (const r of rows) {
            const key = `${r.role}/${r.page}`;
            const rules = pages.get(key) ?? new Map();

            rules.set(`${sc} ${r.rule}`, (rules.get(`${sc} ${r.rule}`) ?? 0) + r.nodes);
            pages.set(key, rules);
        }
    }

    return pages;
}

function pagesScanned(dir) {
    // A page with no violations is absent from summary-by-sc.json; list scanned pages from the folders instead.
    if (!fs.statSync(dir).isDirectory()) {
        return null;
    }

    const found = new Set();

    for (const role of fs.readdirSync(dir)) {
        const roleDir = path.join(dir, role);

        if (!fs.statSync(roleDir).isDirectory()) {
            continue;
        }

        for (const page of fs.readdirSync(roleDir)) {
            if (fs.existsSync(path.join(roleDir, page, 'axe.json'))) {
                found.add(`${role}/${page}`);
            }
        }
    }

    return found;
}

const before = byPage(readJson(summaryFile(beforeArg)));
const after = byPage(readJson(summaryFile(afterArg)));
const scannedBefore = pagesScanned(beforeArg);
const scannedAfter = pagesScanned(afterArg);
const allPages = [...new Set([...before.keys(), ...after.keys(), ...(scannedBefore ?? []), ...(scannedAfter ?? [])])].sort();
const sign = (n) => (n > 0 ? `+${n}` : `${n}`);
const totals = {before: 0, after: 0};
const perSc = new Map();

console.log(`axe violations (nodes), ${beforeArg} -> ${afterArg}\n`);

for (const page of allPages) {
    const b = before.get(page) ?? new Map();
    const a = after.get(page) ?? new Map();
    const status = scannedBefore != null && !scannedBefore.has(page) ? ' (new page)'
        : scannedAfter != null && !scannedAfter.has(page) ? ' (not scanned in the second run)' : '';
    const lines = [];

    for (const rule of [...new Set([...b.keys(), ...a.keys()])].sort()) {
        const nb = b.get(rule) ?? 0;
        const na = a.get(rule) ?? 0;
        const sc = rule.split(' ')[0];
        const s = perSc.get(sc) ?? {before: 0, after: 0};

        s.before += nb;
        s.after += na;
        perSc.set(sc, s);
        totals.before += nb;
        totals.after += na;

        if (nb !== na) {
            lines.push(`  ${rule.padEnd(46)} ${String(nb).padStart(4)} -> ${String(na).padStart(4)}  (${sign(na - nb)})`);
        }
    }

    if (lines.length > 0 || status !== '') {
        console.log(`${page}${status}`);
        lines.forEach((l) => console.log(l));
        if (lines.length === 0) {
            console.log('  no change in violations');
        }
    }
}

console.log('\nPer success criterion');

for (const [sc, s] of [...perSc.entries()].sort()) {
    console.log(`  ${sc.padEnd(14)} ${String(s.before).padStart(4)} -> ${String(s.after).padStart(4)}  (${sign(s.after - s.before)})`);
}

console.log(`  ${'total'.padEnd(14)} ${String(totals.before).padStart(4)} -> ${String(totals.after).padStart(4)}  (${sign(totals.after - totals.before)})`);

const cb = readJson(checksFile(beforeArg));
const ca = readJson(checksFile(afterArg));

if (cb != null && ca != null) {
    console.log('\nScripted checks (summary-checks.json), changed values only');

    for (const page of [...new Set([...Object.keys(cb.pages), ...Object.keys(ca.pages)])].sort()) {
        const b = cb.pages[page] ?? {};
        const a = ca.pages[page] ?? {};
        const changed = [...new Set([...Object.keys(b), ...Object.keys(a)])]
            .filter((k) => JSON.stringify(b[k]) !== JSON.stringify(a[k]))
            .map((k) => `${k}: ${JSON.stringify(b[k])} -> ${JSON.stringify(a[k])}`);

        if (changed.length > 0) {
            console.log(`${page}\n  ${changed.join('\n  ')}`);
        }
    }
} else if (ca != null || cb != null) {
    console.log('\n(summary-checks.json is only in one of the two runs; scripted checks not compared)');
}
