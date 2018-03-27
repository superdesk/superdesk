#!/usr/bin/env python3

"""Parse products xls and generates json for data/vocabularies.json file.

"""

import sys
import json
import openpyxl

family_set = set ()
basic_set = set()
leaf_set = set()
items = []

wb = openpyxl.load_workbook(sys.argv[1], read_only=True)
for sheet in wb:
    for line in sheet.rows:
        if line[0].row == 1:
            continue  # skip header

        code = line[0].value
        family = line[2].value
        basic = line[3].value
        leaf = line[4].value
        output_code = line[8].value

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
