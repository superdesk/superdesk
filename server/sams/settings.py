#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2020 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""SAMS specific settings"""

SAMS_AUTH_TYPE = 'sams.auth.public'

# The following is to be removed once fireq SAMS env. var issues are resolved
SAMS_HOST = 'localhost'
SAMS_PORT = '5700'
SAMS_URL = 'http://localhost:5700'
SAMS_MONGO_DBNAME = 'sd-sams_sams'
SAMS_MONGO_URI = 'mongodb://data-sd/sd-sams_sams'
SAMS_ELASTICSEARCH_URL = 'http://data-sd:9201'
SAMS_ELASTICSEARCH_INDEX = 'sd-sams_sams'
STORAGE_DESTINATION_1 = 'MongoGridFS,Default,mongodb://data-sd/sd-sams_sams'
STORAGE_DESTINATION_2 = 'MongoGridFS,Media,mongodb://data-sd/sd-sams_sams'
STORAGE_DESTINATION_3 = 'MongoGridFS,Publications,mongodb://data-sd/sd-sams_sams'
STORAGE_DESTINATION_4 = 'MongoGridFS,Files,mongodb://data-sd/sd-sams_sams'
