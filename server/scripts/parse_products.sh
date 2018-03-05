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
    family, basic, leaf = cols[1], cols[2], cols[3]

    if family not in family_set:
        family_set.add(family)
        items.append({
            'is_active': True,
            'name': family,
            'qcode': family,
        })

    if basic not in basic_set:
        basic_set.add(basic)
        items.append({
            'is_active': True,
            'name': basic,
            'parent': family,
            'qcode': '%s:%s' % (family, basic),
        })

    if leaf not in leaf_set:
        leaf_set.add(leaf)
        items.append({
            'is_active': True,
            'name': leaf,
            'parent': '%s:%s' % (family, basic),
            'qcode': '%s:%s:%s' % (family, basic, leaf),
        })

print(json.dumps(items, indent=2))
# print('total', len(family_set), len(basic_set), len(leaf_set))
