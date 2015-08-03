# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import json
import os


def _load_json(file_path):
    """
    Reads JSON string from the file located in file_path.

    :param file_path: path of the file having JSON string.
    :return: JSON Object
    """
    with open(file_path, 'r') as f:
        return json.load(f)


_dir_name = os.path.dirname(os.path.realpath(__file__))
_locators_file_path = os.path.join(_dir_name, 'data', 'locators.json')
locators = _load_json(_locators_file_path)
