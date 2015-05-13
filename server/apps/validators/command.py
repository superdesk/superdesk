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
import superdesk
import logging
from superdesk import get_resource_service


logger = logging.getLogger(__name__)


def populate_validators(json_data):
    service = get_resource_service('validators')
    for item in json_data:
        id_name = item.get("_id")

        if service.find_one(_id=id_name, req=None):
            service.put(id_name, item)
        else:
            service.post([item])


def process_validators(filepath):
    """
    This function upserts the validators into the validators collections.
    The format of the file used is JSON.
    :param filepath: absolute filepath
    :return: nothing
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError

    with open(filepath, 'rt') as validators:
        json_data = json.loads(validators.read())
        populate_validators(json_data)


class ValidatorsPopulateCommand(superdesk.Command):
    """
    Class defining the populate validators command.
    """
    option_list = (
        superdesk.Option('--filepath', '-f', dest='filepath', required=True),
    )

    def run(self, filepath):
        process_validators(filepath)


superdesk.command('validators:populate', ValidatorsPopulateCommand())
