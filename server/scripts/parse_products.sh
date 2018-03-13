#!/usr/bin/env python3

"""Parse products cvs and generates json for data/vocabularies.json file.

Use `;` as separator.
"""

import json
import fileinput

skip = 2

family_set = set ()
basic_set = set()
leaf_set = set()
items = []

for line in fileinput.input():
    if skip:
        skip -= 1
        continue

    cols = [col.strip(' "') for col in line.split(';')]
    code, family, basic, leaf = cols[0], cols[2], cols[3], cols[4]

    if family not in family_set:
        family_set.add(family)
        items.append({
            'is_active': True,
            'name': family,
            'qcode': code[:3],
        })

    if basic not in basic_set:
        basic_set.add(basic)
        items.append({
            'is_active': True,
            'name': basic,
            'parent': code[:3],
            'qcode': code[:8],
        })

    if leaf not in leaf_set:
        leaf_set.add(leaf)
        items.append({
            'is_active': True,
            'name': leaf,
            'parent': code[:8],
            'qcode': code,
        })

print(json.dumps(items, indent=2))
