# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import os
from superdesk import json
from datetime import datetime


def load_codes(filename):
    with open(filename, 'r') as f:
        codes = json.load(f)
        return codes


dirname = os.path.dirname(os.path.realpath(__file__))
dirname = os.path.split(dirname)[0]
data_subjects = os.path.join(dirname, 'data', 'subjects.json')
subjects = load_codes(data_subjects)


def init_app(app):
    last_modified = datetime(2012, 7, 10)
    app.subjects.register(subjects, last_modified, True)
