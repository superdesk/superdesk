# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""Whatsapp io service."""

import logging

from superdesk.io.ingest_service import IngestService
from superdesk.utc import utcnow
from superdesk.errors import IngestApiError
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, GUID_TAG
from superdesk.metadata.utils import generate_guid

from .whatsapp_collector import collect_messages


logger = logging.getLogger(__name__)
CREDENTIALS = ("491771781387", "m52HvXhrwyuNllcCUjRDyZDuVIw=")


def set_item_defaults(item):
    item['urgency'] = 5
    item['pubstatus'] = 'usable'
    item['anpa_category'] = [{'qcode': 'e'}]
    item['subject'] = [{'qcode': '01000000', 'name': 'arts, culture and entertainment'}]


class WhatsappIngestService(IngestService):
    """Whatsapp ingest service."""

    PROVIDER = 'whatsapp'

    ERRORS = [IngestApiError.apiTimeoutError().get_error_description(),
              IngestApiError.apiRedirectError().get_error_description(),
              IngestApiError.apiRequestError().get_error_description(),
              IngestApiError.apiUnicodeError().get_error_description(),
              IngestApiError.apiParseError().get_error_description(),
              IngestApiError.apiGeneralError().get_error_description()]

    DATE_FORMAT = '%Y.%m.%d.%H.%M'
    URL = 'http://rmb.reuters.com/rmd/rest/xml'
    token = None

    def __init__(self):
        pass

    def prepare_href(self, href):
        return href

    def _update(self, provider):
        """Service update call."""

        config = provider.get('config', {})
        phone = config.get('phone', None)
        password = config.get('password', None)
        if not phone or not password:
            raise Exception('Credentials are missing')

        messages = collect_messages(phone, password)

        updated = utcnow()

        items = []

        for message in messages:
            item = {}
            set_item_defaults(item)
            item['guid'] = generate_guid(type=GUID_TAG)
            item['versioncreated'] = updated

            item['original_source'] = message['from']
            item['firstcreated'] = message['timestamp']
            item['headline'] = message.get('body', None)

            if message['type'] == 'image':
                item[ITEM_TYPE] = CONTENT_TYPE.PICTURE
                item['renditions'] = {
                    'baseImage': {
                        'href': message['url']
                    }
                }
            else:
                item[ITEM_TYPE] = CONTENT_TYPE.TEXT
                item['body_html'] = message.get('body', None)

            items.append(item)

        yield items
