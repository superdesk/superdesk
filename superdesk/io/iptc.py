"""IPTC module"""

import os
from superdesk import json


def load_codes(filename):
    with open(filename, 'r') as f:
        codes = json.load(f)
        return codes


dirname = os.path.dirname(os.path.realpath(__file__))
data_subject_codes = os.path.join(dirname, 'data', 'subject_codes.json')
subject_codes = load_codes(data_subject_codes)
