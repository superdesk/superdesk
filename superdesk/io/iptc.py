"""IPTC module"""

import os
from superdesk import json

def load_codes():
    dirname = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dirname, 'data', 'subject_codes.json')
    with open(filename, 'r') as f:
        codes = json.load(f)
    return codes

subject_codes = load_codes()
