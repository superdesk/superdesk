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


def populate_vocabularies(json_data):
    service = get_resource_service('vocabularies')
    for item in json_data:
        id_name = item.get("_id")

        if service.find_one(_id=id_name, req=None):
            service.put(id_name, item)
        else:
            service.post([item])


def process_vocabularies(filepath):
    """
    This function upserts the vocabularies into the vocabularies collections.
    The format of the file used is JSON.
    :param filepath: absolute filepath
    :return: nothing
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError

    with open(filepath, 'rt') as vocabularies:
        json_data = json.loads(vocabularies.read())
        populate_vocabularies(json_data)


class VocabulariesPopulateCommand(superdesk.Command):
    """
    Class defining the populate vocabularies command.
    """
    option_list = (
        superdesk.Option('--filepath', '-f', dest='filepath', required=True),
    )

    def run(self, filepath):
        process_vocabularies(filepath)


superdesk.command('vocabularies:populate', VocabulariesPopulateCommand())
