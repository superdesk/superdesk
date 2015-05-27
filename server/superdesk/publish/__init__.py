# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from superdesk.celery_app import celery
from superdesk.publish.publish_content import PublishContent

logger = logging.getLogger(__name__)

transmitters = {}
transmitter_errors = {}


def register_transmitter(transmitter_type, transmitter, errors):
    transmitters[transmitter_type] = transmitter
    transmitter_errors[transmitter_type] = dict(errors)


@celery.task()
def transmit():
    PublishContent().run()


# must be imported for registration
import superdesk.publish.ftp  # NOQA
import superdesk.publish.email  # NOQA
import superdesk.publish.odbc  # NOQA
import superdesk.publish.file_output  # NOQA
import superdesk.publish.publicapi  # NOQA
