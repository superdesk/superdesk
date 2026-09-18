#!/usr/bin/env python3
"""Generate client/briefdesk/terminology.js from the upstream gettext catalogues.

Reads the .pot / .po templates straight out of the reference checkouts with
`git show origin/develop:<path>` (their working trees are stale), applies the
word rules in terminology-rules.json to every msgid, and writes the msgids that
actually change as a CommonJS module for `appConfig.langOverride.en`.

Runtime contract this generator has to satisfy (verified in superdesk-client-core
origin/develop):

- `scripts/init.ts` and `scripts/reload-language.ts` do
  `Object.assign(DEFAULT_ENGLISH_TRANSLATIONS, langOverride.en)`, so the keys are
  the raw msgids, matched exactly.
- `scripts/core/utils.tsx` feeds that object to gettext.js and interpolates
  `{{placeholder}}` only after the lookup, so placeholders must survive verbatim
  and are part of the key.
- gettext.js `dcnpgettext` accepts a **string** value for `gettext()` and only an
  **array** value for `ngettext()`. A msgid with a msgid_plural therefore has to
  be emitted as `[singular, plural]`, and a msgid without one as a plain string.
- `scripts/core/services/translate.ts` hands the same object to angular-gettext's
  `gettextCatalog.setStrings`, so the `translate` directive and filter in Angular
  templates resolve against these keys too.

Usage:
    python3 build-terminology.py [--repos-dir DIR] [--out FILE] [--report]
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPOS_DIR = os.environ.get(
    'BRIEFDESK_REPOS_DIR',
    '/Users/eos87/code/SourceFabric/Superdesk/Core',
)

# Everything that must come through a replacement untouched. Masked before the
# rules run and restored afterwards. The sentinel has no letters in it, so the
# letter-boundary lookarounds in the rules cannot straddle it.
PROTECTED = re.compile(
    r'\{\{[^{}]*\}\}'          # angular / gettext placeholder
    r'|\{[^{}]*\}'             # bare brace placeholder
    r'|%\([^()]*\)[a-z]'       # python named placeholder
    r'|%\d+'                   # gettext.js strfmt placeholder
    r'|%[sdf]'                 # printf placeholder
    r'|<[^<>]+>'               # html tag
    r'|&[a-zA-Z#0-9]+;'        # html entity
)

PO_FIELD = re.compile(r'^(msgid_plural|msgid|msgstr(?:\[\d+\])?|msgctxt)[ \t]+"(.*)"[ \t]*$')
PO_CONT = re.compile(r'^[ \t]*"(.*)"[ \t]*$')

# "a" before these needs no correction even though they start with a vowel
# letter, and "an" before these even though they start with a consonant letter.
CONSONANT_SOUND_PREFIXES = ('eu', 'one', 'once', 'uni', 'use', 'usu', 'uti', 'ubiq', 'ufo', 'url', 'ui')
VOWEL_SOUND_WORDS = ('hour', 'honest', 'honour', 'honor', 'heir')


def po_decode(raw):
    return json.loads('"' + raw + '"')


def parse_po(text):
    """Return the list of {msgid, msgid_plural} entries in a .po/.pot file."""
    entries = []
    cur = {}
    key = None
    buf = []

    def flush():
        nonlocal key, buf
        if key is not None:
            cur[key] = ''.join(buf)
        key = None
        buf = []

    def commit():
        nonlocal cur
        flush()
        if cur.get('msgid'):
            entries.append(cur)
        cur = {}

    for line in text.split('\n'):
        line = line.rstrip('\r')
        if not line.strip():
            commit()
            continue
        if line.startswith('#'):
            flush()
            continue
        m = PO_FIELD.match(line)
        if m:
            if m.group(1) == 'msgid' and 'msgid' in cur:
                commit()
            flush()
            key = m.group(1)
            buf = [po_decode(m.group(2))]
            continue
        m = PO_CONT.match(line)
        if m and key is not None:
            buf.append(po_decode(m.group(1)))
    commit()
    return entries


def git_show(repo, ref_path):
    return subprocess.run(
        ['git', '-C', repo, 'show', ref_path],
        check=True, capture_output=True, text=True,
    ).stdout


def mask(text):
    holes = []

    def take(m):
        holes.append(m.group(0))
        return '\x00%d\x00' % (len(holes) - 1)

    return PROTECTED.sub(take, text), holes


def unmask(text, holes):
    return re.sub(r'\x00(\d+)\x00', lambda m: holes[int(m.group(1))], text)


def build_pattern(source):
    """Word-bounded, case-insensitive, whitespace-flexible literal matcher.

    The lookarounds spell the boundary out instead of using \\b so that "desk(s)"
    and "desk:" still match while "desktop", "Superdesk", "production",
    "incorrect" and identifiers such as "fetch_endpoint" or "article_defaults"
    do not.
    """
    parts = [re.escape(word) for word in source.split()]
    return re.compile(
        r'(?<![A-Za-z0-9_])' + r'\s+'.join(parts) + r'(?![A-Za-z0-9_])',
        re.IGNORECASE,
    )


def apply_case(matched, replacement):
    letters = [c for c in matched if c.isalpha()]
    if letters and all(c.isupper() for c in letters):
        return replacement.upper()
    if letters and all(c.islower() for c in letters):
        return replacement
    if replacement:
        return replacement[0].upper() + replacement[1:]
    return replacement


class Terminology:
    def __init__(self, spec):
        self.rules = []
        for rule in spec['rules']:
            self.rules.append({
                'name': rule['name'],
                'pattern': build_pattern(rule['from']),
                'to': rule['to'],
            })
        self.overrides = spec.get('overrides', {})
        self.skip = set(spec.get('skip', []))
        self.exclusions = {k: set(v) for k, v in spec.get('exclusions', {}).items()}
        self.head_words = {r['to'].split()[0].lower() for r in spec['rules'] if r['to'].strip()}
        self.article_fix = re.compile(
            r'(?<![A-Za-z])([Aa]n?)(\s+)([A-Za-z][A-Za-z-]*)',
        )
        self.used = set()

    def _needs_an(self, word):
        low = word.lower()
        if low.startswith(VOWEL_SOUND_WORDS):
            return True
        if low.startswith(CONSONANT_SOUND_PREFIXES):
            return False
        return low[0] in 'aeiou'

    def _fix_articles(self, text):
        def repl(m):
            article, gap, word = m.group(1), m.group(2), m.group(3)
            if word.lower() not in self.head_words:
                return m.group(0)
            want = 'an' if self._needs_an(word) else 'a'
            if article[0].isupper():
                want = want.capitalize()
            return want + gap + word

        return self.article_fix.sub(repl, text)

    def convert(self, source, skipped=()):
        text, holes = mask(source)
        for rule in self.rules:
            if rule['name'] in skipped:
                continue
            new = rule['pattern'].sub(
                lambda m, to=rule['to']: apply_case(m.group(0), to),
                text,
            )
            if new != text:
                self.used.add(rule['name'])
                text = new
        text = self._fix_articles(text)
        return unmask(text, holes)


def collect_msgids(spec, repos_dir):
    """Merge every source catalogue into {msgid: msgid_plural or None}."""
    merged = {}
    conflicts = []
    for source in spec['sources']:
        repo = os.path.join(repos_dir, source['repo'])
        text = git_show(repo, 'origin/develop:' + source['path'])
        for entry in parse_po(text):
            msgid = entry['msgid']
            plural = entry.get('msgid_plural') or None
            if msgid in merged:
                if merged[msgid] != plural and plural is not None and merged[msgid] is None:
                    conflicts.append(msgid)
                    merged[msgid] = plural
                elif merged[msgid] is not None and plural is None:
                    conflicts.append(msgid)
            else:
                merged[msgid] = plural
    return merged, conflicts


def js_string(value):
    return json.dumps(value, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repos-dir', default=DEFAULT_REPOS_DIR)
    ap.add_argument('--rules', default=os.path.join(HERE, 'terminology-rules.json'))
    ap.add_argument('--out', default=os.path.join(HERE, 'terminology.js'))
    ap.add_argument('--report', action='store_true', help='print every pair to stderr')
    args = ap.parse_args()

    with open(args.rules, encoding='utf-8') as f:
        spec = json.load(f)

    merged, conflicts = collect_msgids(spec, args.repos_dir)
    term = Terminology(spec)

    result = {}
    problems = []
    for msgid in sorted(merged):
        if msgid in term.skip:
            continue
        plural = merged[msgid]
        skipped = term.exclusions.get(msgid, ())
        override = term.overrides.get(msgid)

        if plural is None:
            new_singular = override if isinstance(override, str) else term.convert(msgid, skipped)
            if new_singular != msgid:
                result[msgid] = new_singular
            sources = [(msgid, new_singular)]
        else:
            if isinstance(override, list):
                new_singular, new_plural = override
            else:
                new_singular = term.convert(msgid, skipped)
                new_plural = term.convert(plural, skipped)
            if new_singular != msgid or new_plural != plural:
                result[msgid] = [new_singular, new_plural]
            sources = [(msgid, new_singular), (plural, new_plural)]

        for source, target in sources:
            _, source_holes = mask(source)
            _, target_holes = mask(target)
            if sorted(source_holes) != sorted(target_holes):
                problems.append((source, target))

    if problems:
        for msgid, candidate in problems:
            sys.stderr.write('PLACEHOLDER DRIFT: %r -> %r\n' % (msgid, candidate))
        sys.exit('refusing to write: a replacement changed a placeholder')

    # Strings that never reach a .pot file because the msgid is computed at
    # runtime, typically `item.state | translate` in Angular templates.
    for msgid, value in spec.get('extra', {}).items():
        if value != msgid:
            result[msgid] = value

    unused = [r['name'] for r in spec['rules'] if r['name'] not in term.used]

    lines = [
        '// Generated by build-terminology.py. Do not edit by hand.',
        '// Regenerate: python3 client/briefdesk/build-terminology.py',
        '// Keys are exact English msgids from the upstream gettext catalogues;',
        '// an array value is a [singular, plural] pair for ngettext lookups.',
        '',
        'module.exports = {',
    ]
    for msgid in sorted(result):
        lines.append('    %s: %s,' % (js_string(msgid), js_string(result[msgid])))
    lines.append('};')
    lines.append('')

    with open(args.out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    sys.stderr.write('msgids scanned: %d\n' % len(merged))
    sys.stderr.write('entries written: %d\n' % len(result))
    sys.stderr.write('plural entries: %d\n' % sum(1 for v in result.values() if isinstance(v, list)))
    if unused:
        sys.stderr.write('rules that matched nothing: %s\n' % ', '.join(unused))
    if conflicts:
        sys.stderr.write('msgid used both with and without a plural: %s\n' % ', '.join(map(repr, conflicts)))
    dead = [k for k in term.overrides if k not in merged]
    if dead:
        sys.stderr.write('overrides for unknown msgids: %s\n' % ', '.join(map(repr, dead)))
    dead = [k for k in term.exclusions if k not in merged]
    if dead:
        sys.stderr.write('exclusions for unknown msgids: %s\n' % ', '.join(map(repr, dead)))

    if args.report:
        for msgid in sorted(result):
            sys.stderr.write('%s\n  -> %s\n' % (js_string(msgid), js_string(result[msgid])))


if __name__ == '__main__':
    main()
