
import os
from flask import json
from datetime import datetime


def init_app(app):
    dirname = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(dirname, 'subject_codes_it.json')
    with open(filename, 'r', encoding='utf-8') as f:
        codes = json.load(f)
    last_modified = datetime(2017, 2, 27)
    app.subjects.subjects.clear()
    app.subjects.register(codes, last_modified)
