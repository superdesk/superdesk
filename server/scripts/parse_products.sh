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
    code, family, basic, leaf, output_code = cols[0], cols[2], cols[3], cols[4], cols[8]

    family_code = code[:3]
    basic_code = code[:8]


    if family_code not in family_set:
        family_set.add(family_code)
        items.append({
            'is_active': True,
            'name': family,
            'qcode': family_code,
        })

    if basic_code not in basic_set:
        basic_set.add(basic_code)
        items.append({
            'is_active': True,
            'name': basic,
            'parent': family_code,
            'qcode': basic_code,
        })

    if code not in leaf_set:
        leaf_set.add(code)
        items.append({
            'is_active': True,
            'name': leaf,
            'parent': basic_code,
            'qcode': code,
            'output_code': output_code,
        })

print(json.dumps(items, indent=2))
